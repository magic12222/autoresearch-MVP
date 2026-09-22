# 交接

当前目标：从 AI Scientist 论文机制出发，先实现可信的实验闭环，再逐步扩展成 Web 平台；总体规划见 `PROJECT_PLAN.md`。

当前状态：P0-1 已实现固定样例的本地执行、成功/失败/超时识别、日志/指标/artifact 和追加历史。P1-1 已实现结构化提案输入、Semantic Scholar/OpenAlex 检索和证据保存。验证使用 `python -m unittest discover -s tests -v`；已实际运行三个 CLI 实验样例及提案检索。当前未接入 LLM 或远程实验执行器。

重要边界：P0 只运行审核过的固定样例。用户选小型 2D Diffusion 为后续基线，尚未验证模板和数据。当前本地检索两个 API 均返回 HTTP 429，证据状态为 `insufficient_evidence`，不能宣称想法新颖。`labtmx56` 有 4 张 RTX 3090，但最近只读检查时 GPU 忙；服务器环境和资源使用规则尚待核实。Git 仅本地初始化，未创建远程仓库。

下一步建议：核实 2D Diffusion 官方模板、数据/指标和服务器资源；解决至少一个真实论文检索源的可用性，核对候选论文。再设计 LLM 提案生成、受限代码修改和隔离执行。开放生成代码前需要隔离执行方案。
