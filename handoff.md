# 交接

当前目标：P1-2 原样复现 SakanaAI/AI-Scientist 官方 2D Diffusion baseline，跑通后再做最薄输出 adapter；总体规划见 `PROJECT_PLAN.md`，复现契约见 `docs/reproduction-ai-scientist-2d-diffusion.md`。

当前状态：P0-1 与 P1-1 保持不变。AI-Scientist `1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb` 和 NPEET `8b0d9485423f74e5eb199324cf362765596538d3` 已作为独立 submodule 固定；官方模板结构、依赖、输入输出、指标、命令和许可已记录。尚未接入 LLM、Web 或任意命令执行器，也尚未运行 GPU baseline。

重要边界：P0 仍只运行审核过的固定样例；官方实验逻辑不得修改，adapter 只能在 baseline 成功后读取输出。AI-Scientist 当前使用带限制与论文披露要求的自定义许可证。当前本地检索两个 API 均返回 HTTP 429，证据状态为 `insufficient_evidence`，不能宣称想法新颖。`labtmx56` 的 2026-09-22 记录显示 4 张 RTX 3090 当时全忙；2026-09-23 新一次 SSH 连接超时，当前环境、磁盘和占用未知。项目已有 GitHub remote，但本轮变更尚未提交或推送。

下一步：恢复 `labtmx56` 连接并只读运行 GPU/CUDA/Python/conda/磁盘/占用检查；确认资源规则和空闲 GPU 后，在独立 upstream 目录按固定 commit 配置 Python 3.11、官方依赖和 NPEET，原样运行两条 baseline 命令并保存完整证据。成功后实现独立导入 adapter，不改 P0 runner。开放生成代码前仍需隔离执行方案。
