# 2026-09-23 服务器预检记录

本目录是 `labtmx56`（主机名 `3090-1`）上 AI Scientist 官方 2D Diffusion baseline 的预检与环境证据快照。采集时尚未运行 baseline，也没有 `run_0`、metrics 或 plots。

远端 reference root：`/data/tangmingxue/experiments/ai-scientist-2d-diffusion`。

- `system-preflight.txt`：系统、磁盘、内存、commit、Python/conda 和计划执行命令。
- `nvidia-smi-preflight.txt`、`gpu-preflight.csv`、`gpu-processes-preflight.txt`：GPU、占用和进程归属。
- `pip-freeze.txt`、`conda-list.txt`：实际环境版本。
- `setup.log`、`dependencies.log`：环境创建与依赖安装原始输出。
- `experiment-help.txt`：官方 `experiment.py --help` 输出。

完整官方 `requirements.txt` 因未锁定的 `aider-chat` 与当前包生态发生长时间依赖回溯，已人工中止并保留日志。随后按 `templates/2d_diffusion` 的实际 imports 安装最小运行依赖和固定 NPEET；`pip check`、imports 和 `experiment.py --help` 均通过。

采集时四张 RTX 3090 都有现存任务，因此没有启动训练。GPU 0/1 属于其他用户；GPU 2/3 是当前用户的 PPO/Ray 任务。
