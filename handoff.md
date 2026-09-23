# 交接

当前目标：P1-2 原样复现 SakanaAI/AI-Scientist 官方 2D Diffusion baseline，跑通后再做最薄输出 adapter；总体规划见 `PROJECT_PLAN.md`，复现契约见 `docs/reproduction-ai-scientist-2d-diffusion.md`。

当前状态：P0-1 与 P1-1 保持不变。AI-Scientist 和 NPEET 已固定；`labtmx56` 上的独立 reference、conda/Python 3.11.16、PyTorch 2.14.0+cu130 和 baseline 最小依赖已准备并通过 imports、`pip check`、`experiment.py --help`。原始预检证据已同步到 `reproductions/ai-scientist-2d-diffusion/2026-09-23-preflight/`。尚未接入 LLM、Web 或任意命令执行器，也尚未运行 GPU baseline。

重要边界：P0 仍只运行审核过的固定样例；官方实验逻辑不得修改，adapter 只能在 baseline 成功后读取输出。AI-Scientist 使用带限制与论文披露要求的自定义许可证。完整顶层 requirements 当前会在 `aider-chat` 上长时间回溯，本次只安装模板实际 imports。预检时四张 GPU 均有任务：GPU 0/1 属于其他用户，GPU 2/3 是当前用户的 PPO/Ray 任务；不得抢占。当前本地检索两个 API 仍为 HTTP 429，不能宣称想法新颖。

下一步：确认一张 GPU 真正空闲且可使用后，在 `/data/tangmingxue/experiments/ai-scientist-2d-diffusion/AI-Scientist/templates/2d_diffusion` 用独立环境原样运行两条 baseline 命令并保存完整证据。成功后实现独立导入 adapter，不改 P0 runner。开放生成代码前仍需隔离执行方案。
