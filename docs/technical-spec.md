# 技术规格

P0 使用本地 Windows Python 3.11.4，标准库实现，`pyproject.toml` 声明 Python >=3.11 且无运行依赖。源码位于 `src/research_platform/`；入口 `p0.py`。验证使用标准库 `unittest`，无需安装包。

持久数据位于项目内 `workspace/`，按 run 独立存放；`manifest.json` 是单次记录，`journal.jsonl` 是追加索引。固定样例位于 `examples/`。执行子进程只继承基础运行环境变量，不继承模型或 SSH 凭据变量。P0 不提供任意命令入口。

远程 `labtmx56` 为 Linux/Python 3.12.3，拥有 4 张 RTX 3090；作为后续训练资源，当前不部署项目。其默认 Python 无 PyTorch，容器和调度环境未确认。

P1 第一小步继续使用标准库 `urllib` 调用 [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/snippets) 和 [OpenAlex Works API](https://developers.openalex.org/)；单请求最多 5 条、12 秒、2 MB。Semantic Scholar 可选密钥只从 `S2_API_KEY` 环境变量读取并放入请求头，不保存到日志。原始响应及规范化证据保存在 `workspace/novelty_checks/`。本机实际调用均返回 HTTP 429；只读检查中服务器向 OpenAlex 请求返回 HTTP 200，向 Semantic Scholar 请求返回 HTTP 429。尚未把服务器用作平台检索代理。
