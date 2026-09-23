# 当前需求与验收

## 已确认目标

先复现 AI Scientist 科研核心，再开发类似 Polaris 的 Web 平台。首个实现任务 P0-1 是受控实验执行记录，不运行大规模训练，不做 UI。完整阶段见 `../PROJECT_PLAN.md`。

## P0-1 验收

- 从固定样例创建独立实验 ID 和工作目录。
- 成功、非零退出和超时都留存命令、代码快照、时间、stdout/stderr 和状态。
- 成功实验保存数值指标和 artifact 清单；失败实验保留错误。
- 能从追加日志重读完整历史，且不将凭据传入样例进程。

当前不包含 LLM、任意代码执行、服务器训练、数据库、网页或论文生成。

## P1 第一小步：提案与检索证据

- 读取包含标题、动机、假设、方法、实验计划、预期结果和搜索词的结构化提案。
- 按搜索词调用公开论文检索源，保存原始响应、标准化候选论文及查询来源。
- 对 429 或网络错误保留失败状态；证据不足时不得自动宣称“新颖”。

选定的小型研究基线为 2D Diffusion，但示例提案仅用于验证接口，尚未完成真实训练、文献比对或想法自动生成。

## P1-2：官方 2D Diffusion baseline

- 以独立 Git submodule 固定 SakanaAI/AI-Scientist 和 NPEET，不把官方源码散拷到平台模块。
- 在 `labtmx56` 上先只读核实 GPU、CUDA、Python/conda、磁盘和占用；资源不明或 GPU 繁忙时不得启动训练。
- 按官方 README 配置 Python 3.11、项目依赖和 NPEET，在固定 commit 的 `templates/2d_diffusion` 中原样运行 `python experiment.py --out_dir run_0` 与 `python plot.py`。
- 不修改官方实验逻辑；保存完整命令、commit、环境/GPU、时长、退出码、stdout/stderr、目录树、原始 metrics、图和 artifact 哈希。
- baseline 成功后才实现只读导入 adapter，将官方输出映射到 ExperimentRun/journal；不得借此把 P0 CLI 开放为任意命令入口。

详细复现契约见 `reproduction-ai-scientist-2d-diffusion.md`。本阶段不接 LLM，不做 Web，不生成论文。
