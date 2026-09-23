# AI Scientist 官方 2D Diffusion baseline 复现

## 1. 目标与边界

P1-2 只复现 SakanaAI/AI-Scientist 官方 `templates/2d_diffusion` baseline，并在成功后设计一个只读、最薄的输出 adapter。官方实验逻辑、默认参数、数据集和指标不作修改；不接 LLM，不做 Web，不把 P0 CLI 扩展为任意命令入口。

官方代码作为独立 Git submodule 保存在 `upstream/AI-Scientist`，NPEET 作为独立依赖 submodule 保存在 `upstream/NPEET`。平台源码只保存复现元数据和后续 adapter，不散拷官方源码。

## 2. 固定版本与许可

核验日期：2026-09-23。

| 对象 | 固定版本 | 上游分支 | 许可 |
| --- | --- | --- | --- |
| SakanaAI/AI-Scientist | `1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb` | `main` | The AI Scientist Source Code License v1.0，2025-12；包含用途限制和科学论文显著披露要求 |
| gregversteeg/NPEET | `8b0d9485423f74e5eb199324cf362765596538d3`，项目版本 `1.0.1` | `master` | MIT |

AI-Scientist 当前没有 GitHub Release，故以完整 commit SHA 标识版本。若以后分发其代码或衍生物，必须保留完整许可证并重新核对限制；若使用 The AI Scientist 生成或传播论文，必须遵守显著披露条款。本阶段只运行人工指定的官方 baseline，不生成论文。

## 3. 官方代码结构

| 路径 | 作用 |
| --- | --- |
| `experiment.py` | DDPM 训练与评估入口；接受 `--out_dir` 和训练超参数；自动选择 CUDA，否则退回 CPU |
| `datasets.py` | 构造 `circle`、`line`、`moons`、`dino` 四个二维数据集 |
| `DatasaurusDozen.tsv` | 随仓提供的 dino 原始数据 |
| `ema_pytorch.py` | 模板内置 EMA 实现 |
| `plot.py` | 扫描当前目录下所有 `run*` 目录并生成训练损失图和样本散点图 |
| `prompt.json` | 完整 AI Scientist 流程使用的模板任务描述；baseline 不读取 |
| `seed_ideas.json`、`ideas.json` | 想法示例/历史；baseline 不读取 |
| `latex/` | 论文模板；baseline 不读取 |

## 4. 输入、计算与依赖

默认命令只显式输入 `--out_dir run_0`。其余官方默认值是：batch size 256、eval batch size 10,000、learning rate `3e-4`、100 个 diffusion timesteps、每个数据集 10,000 个训练步、线性 beta schedule、128 维 embedding、256 hidden size、3 个 residual hidden layers。

四个数据集均取 100,000 个二维样本。数据生成使用固定的 NumPy/sklearn seed 42，但模型初始化、DataLoader 顺序、训练噪声和采样没有统一设置随机种子，因此不同运行的 loss、KL 和图像不会严格逐位复现。

直接依赖为 Python、PyTorch、NumPy、pandas、scikit-learn、SciPy、NPEET、matplotlib 和 tqdm。官方顶层 `requirements.txt` 未锁版本，还包含完整流程所需的 LLM、数据集和写作依赖；最终记录必须保存实际安装版本和 `pip freeze`。NPEET 的 `pyproject.toml` 声明依赖 NumPy、SciPy、scikit-learn。

## 5. 输出与指标

实验在 `run_0/` 写入：

- `final_info.json`：每个数据集的 `training_time`、`eval_loss`、`inference_time`、`kl_divergence`。
- `all_results.pkl`：每个数据集的逐步训练 loss 和 10,000 个生成样本。

`plot.py` 在模板目录写入 `train_loss.png` 和 `generated_images.png`。`eval_loss` 是整个训练数据 DataLoader 上的噪声预测 MSE；`kl_divergence` 是 NPEET `kldiv(real_data, sample, k=5)` 的非参数估计，越低通常越好。时间指标主要用于同机比较。

`all_results.pkl` 是 Python pickle；adapter 不应把任意来源的 pickle 当作安全输入。baseline 映射优先只解析 JSON，并将 pickle 作为不可解释 artifact 记录哈希。

## 6. 服务器只读预检

在创建环境或克隆代码前执行：

```bash
nvidia-smi
nvidia-smi --query-gpu=index,name,uuid,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory --format=csv,noheader
command -v nvcc && nvcc --version
command -v python && python --version
command -v python3 && python3 --version
command -v conda && conda --version
conda env list
df -hT / /home /tmp
free -h
uptime
```

2026-09-23 已完成新一次预检：服务器是 Ubuntu 24.04.4 LTS，NVIDIA driver 595.84，4 张 RTX 3090，磁盘约 818 GiB 可用。采集时四张卡均有现存任务：GPU 0/1 属于其他用户，GPU 2/3 是当前用户的 PPO/Ray 任务；因此未启动 baseline。原始证据保存在 `reproductions/ai-scientist-2d-diffusion/2026-09-23-preflight/`。

## 7. 环境与原样复现命令

远端 reference root 已建立为 `/data/tangmingxue/experiments/ai-scientist-2d-diffusion`，独立环境为其 `env/`。服务器没有可直接调用的 conda；已在 `/data/tangmingxue/tools/miniconda3` 安装用户级 conda 26.7.1，并使用 conda-forge 创建 Python 3.11.16 环境，避免代替用户接受 Anaconda 默认 channel 的服务条款。

完整官方 `requirements.txt` 因未锁定的 `aider-chat` 与当前依赖发生大规模版本回溯而中止。随后按模板实际 imports 安装 PyTorch、NumPy、pandas、SciPy、scikit-learn、matplotlib、tqdm 和固定 NPEET。`pip check`、imports 和 `experiment.py --help` 已通过；实际版本见预检目录中的 `pip-freeze.txt`。

用于从空目录重建的命令如下；下面的占位符仍需替换为目标路径：

```bash
git clone https://github.com/SakanaAI/AI-Scientist.git <reference-root>/AI-Scientist
cd <reference-root>/AI-Scientist
git checkout --detach 1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb

conda create --prefix <env-prefix> python=3.11 -y
conda activate <env-prefix>
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

git clone https://github.com/gregversteeg/NPEET.git <reference-root>/NPEET
cd <reference-root>/NPEET
git checkout --detach 8b0d9485423f74e5eb199324cf362765596538d3
python -m pip install .
python -m pip install scikit-learn
```

环境核验：

```bash
python --version
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
python -m pip freeze
nvidia-smi
```

只有确认目标 GPU 空闲且不抢占他人任务后，才原样执行：

```bash
cd <reference-root>/AI-Scientist/templates/2d_diffusion
python experiment.py --out_dir run_0
python plot.py
```

实际执行时由外层 shell 记录开始/结束 UTC 时间、墙钟时间和退出码，并分别保存两条命令的 stdout/stderr；不得编辑 `experiment.py`、`datasets.py`、`ema_pytorch.py` 或 `plot.py`。

## 8. 成功判定与证据清单

1. 固定 commit 可核验，官方 submodule 工作树无实验逻辑改动。
2. `experiment.py` 和 `plot.py` 均退出码 0。
3. `run_0/final_info.json` 可解析，四个数据集均含四个有限数值字段。
4. `run_0/all_results.pkl`、两张 PNG 存在且非空。
5. 保存完整命令、cwd、环境版本、GPU、开始/结束时间、运行时长、stdout/stderr、目录树、文件大小和 SHA-256。
6. 只报告实际值及其方向，不把单次未设全局 seed 的结果声称为严格确定性复现。

## 9. 最薄 adapter 设计（baseline 成功后实现）

adapter 只消费一个已完成的官方 run，不负责启动训练，也不修改 upstream：

1. 输入 upstream commit、远端主机标识、命令、环境摘要、日志路径、`run_0` 路径和绘图路径。
2. 校验退出码、必需文件、JSON schema、有限数值、路径归属和文件哈希。
3. 将四个数据集的四个字段映射为 `dataset.metric` 命名的 ExperimentRun metrics；KL 与 eval loss 标记为 `minimize`，时间为观测型 `minimize`。
4. 记录 JSON、pickle、两张 PNG、stdout/stderr 和环境清单的相对路径、大小及 SHA-256。
5. journal 保留 `source=official_ai_scientist_2d_diffusion`、upstream commit、remote host、原始命令和原始指标文件；不覆盖或伪装成 P0 固定样例。

现有 `ExperimentSpec` 仍限制为三个 P0 样例。adapter 应使用单独的导入契约，不把 P0 runner 改造成任意命令执行器。

## 10. 已知风险

- 当前四张 GPU 均有现存任务，不能安全开始训练；GPU 0/1 还属于其他用户，严禁抢占。
- 官方依赖未锁版本；PyTorch/CUDA 与较新 NumPy/SciPy 组合可能有兼容差异。
- 完整顶层 requirements 当前会在 `aider-chat` 上大规模回溯；本次 baseline 使用按模板 imports 得出的最小依赖集，并保留原始失败日志。
- 官方代码没有统一设置训练/采样 seed，单次指标存在随机波动。
- `plot.py` 会读取当前目录所有 `run*` 目录；复现目录应只含本轮预期 run。
- `plot.py` 调用 `plt.show()`；无图形服务器需确认 matplotlib 后端，但不应修改官方脚本。
- NPEET 的 kNN KL 估计对样本分布和依赖版本敏感。
- `all_results.pkl` 只能在信任固定 upstream 和本轮产物时读取；平台默认不反序列化任意 pickle。
- AI-Scientist 使用自定义限制性许可证；未来分发、衍生或论文生成前需再次核对许可与披露要求。
