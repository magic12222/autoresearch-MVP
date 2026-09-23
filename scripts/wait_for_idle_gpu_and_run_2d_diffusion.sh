#!/usr/bin/env bash

set -euo pipefail

REF_ROOT="${REF_ROOT:-/data/tangmingxue/experiments/ai-scientist-2d-diffusion}"
PYTHON="${PYTHON:-$REF_ROOT/env/bin/python}"
TEMPLATE="$REF_ROOT/AI-Scientist/templates/2d_diffusion"
RECORDS="$REF_ROOT/records"
POLL_SECONDS="${POLL_SECONDS:-30}"
IDLE_SECONDS="${IDLE_SECONDS:-300}"
MAX_MEMORY_USED_MIB="${MAX_MEMORY_USED_MIB:-512}"
MAX_UTILIZATION_PERCENT="${MAX_UTILIZATION_PERCENT:-5}"

usage() {
    echo "用法: $0 [--check-once]"
    echo "默认等待同一张 GPU 连续空闲 300 秒后运行官方 2D Diffusion baseline。"
}

check_once=false
case "${1:-}" in
    "") ;;
    --check-once) check_once=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

for value in "$POLL_SECONDS" "$IDLE_SECONDS" "$MAX_MEMORY_USED_MIB" "$MAX_UTILIZATION_PERCENT"; do
    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        echo "监控参数必须是非负整数。" >&2
        exit 2
    fi
done
if (( POLL_SECONDS == 0 || IDLE_SECONDS == 0 )); then
    echo "POLL_SECONDS 和 IDLE_SECONDS 必须大于 0。" >&2
    exit 2
fi

for command in nvidia-smi flock sha256sum git; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "缺少命令: $command" >&2
        exit 1
    fi
done
if [[ ! -x "$PYTHON" ]]; then
    echo "Python 不可执行: $PYTHON" >&2
    exit 1
fi
if [[ ! -d "$TEMPLATE" ]]; then
    echo "模板目录不存在: $TEMPLATE" >&2
    exit 1
fi

mkdir -p "$RECORDS"
exec 9>"$RECORDS/baseline-monitor.lock"
if ! flock -n 9; then
    echo "已有 baseline 监控或运行进程持有锁。" >&2
    exit 1
fi

monitor_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
monitor_log="$RECORDS/baseline-monitor-$monitor_stamp.log"
exec > >(tee -a "$monitor_log") 2>&1

echo "monitor_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "criteria=no compute process, memory.used <= ${MAX_MEMORY_USED_MIB} MiB, utilization.gpu <= ${MAX_UTILIZATION_PERCENT}%, continuously for ${IDLE_SECONDS}s"
echo "poll_seconds=$POLL_SECONDS"

if [[ -e "$TEMPLATE/run_0" || -e "$TEMPLATE/train_loss.png" || -e "$TEMPLATE/generated_images.png" ]]; then
    echo "检测到已有 run_0 或 baseline 图片；为避免覆盖，脚本退出。" >&2
    exit 1
fi
if find "$TEMPLATE" -maxdepth 1 -mindepth 1 -type d -name 'run*' -print -quit | grep -q .; then
    echo "模板目录存在其他 run* 目录；plot.py 会自动读取它们，为避免混入结果，脚本退出。" >&2
    exit 1
fi

declare -A idle_since=()
selected_gpu=""
selected_uuid=""

sample_gpus() {
    local now index uuid memory_used utilization clean_uuid elapsed
    local -A busy_uuid=()
    while IFS= read -r uuid; do
        clean_uuid="${uuid//[[:space:]]/}"
        [[ -n "$clean_uuid" ]] && busy_uuid["$clean_uuid"]=1
    done < <(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader 2>/dev/null || true)

    now="$(date +%s)"
    while IFS=',' read -r index uuid memory_used utilization; do
        index="${index//[[:space:]]/}"
        uuid="${uuid//[[:space:]]/}"
        memory_used="${memory_used//[[:space:]]/}"
        utilization="${utilization//[[:space:]]/}"
        [[ -z "$index" || -z "$uuid" ]] && continue

        if [[ -z "${busy_uuid[$uuid]+x}" ]] \
            && (( memory_used <= MAX_MEMORY_USED_MIB )) \
            && (( utilization <= MAX_UTILIZATION_PERCENT )); then
            if [[ -z "${idle_since[$index]+x}" ]]; then
                idle_since[$index]="$now"
            fi
            elapsed=$((now - idle_since[$index]))
            echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) gpu=$index idle=${elapsed}s memory_used=${memory_used}MiB utilization=${utilization}%"
            if (( elapsed >= IDLE_SECONDS )) && [[ -z "$selected_gpu" ]]; then
                selected_gpu="$index"
                selected_uuid="$uuid"
            fi
        else
            unset 'idle_since[$index]'
            echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) gpu=$index busy memory_used=${memory_used}MiB utilization=${utilization}% compute_process=${busy_uuid[$uuid]+yes}"
        fi
    done < <(nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader,nounits)
}

while [[ -z "$selected_gpu" ]]; do
    sample_gpus
    if $check_once; then
        echo "check_once_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        exit 0
    fi
    [[ -n "$selected_gpu" ]] && break
    sleep "$POLL_SECONDS"
done

echo "candidate_gpu=$selected_gpu candidate_uuid=$selected_uuid"
echo "等待 2 秒后进行启动前最终复检。"
sleep 2

selected_gpu_before="$selected_gpu"
selected_uuid_before="$selected_uuid"
IFS=',' read -r recheck_uuid recheck_memory recheck_utilization < <(
    nvidia-smi -i "$selected_gpu_before" --query-gpu=uuid,memory.used,utilization.gpu --format=csv,noheader,nounits
)
recheck_uuid="${recheck_uuid//[[:space:]]/}"
recheck_memory="${recheck_memory//[[:space:]]/}"
recheck_utilization="${recheck_utilization//[[:space:]]/}"
if nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader 2>/dev/null | sed 's/[[:space:]]//g' | grep -Fxq "$selected_uuid_before" \
    || [[ "$recheck_uuid" != "$selected_uuid_before" ]] \
    || (( recheck_memory > MAX_MEMORY_USED_MIB )) \
    || (( recheck_utilization > MAX_UTILIZATION_PERCENT )); then
    echo "候选 GPU 在最终复检时不再空闲，退出且不启动训练。" >&2
    exit 1
fi
selected_gpu="$selected_gpu_before"
selected_uuid="$selected_uuid_before"

run_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
run_records="$RECORDS/baseline-$run_stamp"
mkdir -p "$run_records"

{
    echo "run_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "physical_gpu_index=$selected_gpu"
    echo "gpu_uuid=$selected_uuid"
    echo "reference_root=$REF_ROOT"
    echo "template_dir=$TEMPLATE"
    echo "python=$PYTHON"
    echo "ai_scientist_commit=$(git -C "$REF_ROOT/AI-Scientist" rev-parse HEAD)"
    echo "npeet_commit=$(git -C "$REF_ROOT/NPEET" rev-parse HEAD)"
    echo "command_1=CUDA_VISIBLE_DEVICES=$selected_gpu MPLBACKEND=Agg $PYTHON experiment.py --out_dir run_0"
    echo "command_2=CUDA_VISIBLE_DEVICES=$selected_gpu MPLBACKEND=Agg $PYTHON plot.py"
} > "$run_records/manifest.txt"

git -C "$REF_ROOT/AI-Scientist" diff --exit-code -- . > "$run_records/upstream-diff-before.txt"
git -C "$REF_ROOT/AI-Scientist" status --short > "$run_records/upstream-status-before.txt"
"$PYTHON" -m pip freeze > "$run_records/pip-freeze.txt"
nvidia-smi > "$run_records/nvidia-smi-before.txt"
nvidia-smi --query-gpu=index,name,uuid,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv > "$run_records/gpu-before.csv"

cd "$TEMPLATE"
experiment_started_epoch="$(date +%s)"
echo "experiment_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) gpu=$selected_gpu"
set +e
CUDA_VISIBLE_DEVICES="$selected_gpu" MPLBACKEND=Agg "$PYTHON" experiment.py --out_dir run_0 \
    > "$run_records/experiment.stdout.log" \
    2> "$run_records/experiment.stderr.log"
experiment_status=$?
set -e
experiment_finished_epoch="$(date +%s)"
echo "experiment_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) exit_code=$experiment_status"
{
    echo "experiment_exit_code=$experiment_status"
    echo "experiment_duration_seconds=$((experiment_finished_epoch - experiment_started_epoch))"
} >> "$run_records/manifest.txt"
if (( experiment_status != 0 )); then
    echo "experiment.py 失败，退出码 $experiment_status；保留日志且不运行 plot.py。" >&2
    nvidia-smi > "$run_records/nvidia-smi-after-failure.txt" || true
    exit "$experiment_status"
fi

plot_started_epoch="$(date +%s)"
echo "plot_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set +e
CUDA_VISIBLE_DEVICES="$selected_gpu" MPLBACKEND=Agg "$PYTHON" plot.py \
    > "$run_records/plot.stdout.log" \
    2> "$run_records/plot.stderr.log"
plot_status=$?
set -e
plot_finished_epoch="$(date +%s)"
echo "plot_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) exit_code=$plot_status"
{
    echo "plot_exit_code=$plot_status"
    echo "plot_duration_seconds=$((plot_finished_epoch - plot_started_epoch))"
    echo "run_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$run_records/manifest.txt"
if (( plot_status != 0 )); then
    echo "plot.py 失败，退出码 $plot_status；保留实验结果与日志。" >&2
    nvidia-smi > "$run_records/nvidia-smi-after-failure.txt" || true
    exit "$plot_status"
fi

"$PYTHON" -c 'import json, math, pathlib; p=pathlib.Path("run_0/final_info.json"); d=json.loads(p.read_text()); expected={"circle","dino","line","moons"}; assert set(d)==expected; keys={"training_time","eval_loss","inference_time","kl_divergence"}; assert all(set(d[n]["means"])==keys for n in expected); assert all(math.isfinite(float(v)) for n in expected for v in d[n]["means"].values()); print(json.dumps(d, indent=2, sort_keys=True))' > "$run_records/validated-metrics.json"

nvidia-smi > "$run_records/nvidia-smi-after.txt"
nvidia-smi --query-gpu=index,name,uuid,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv > "$run_records/gpu-after.csv"
git -C "$REF_ROOT/AI-Scientist" diff --exit-code -- . > "$run_records/upstream-diff-after.txt"
git -C "$REF_ROOT/AI-Scientist" status --short > "$run_records/upstream-status-after.txt"
find run_0 -printf '%y %p %s bytes\n' | sort > "$run_records/run_0-tree.txt"
sha256sum run_0/final_info.json run_0/all_results.pkl train_loss.png generated_images.png > "$run_records/artifacts.sha256"
cp run_0/final_info.json "$run_records/final_info.json"

echo "baseline_succeeded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "records=$run_records"
