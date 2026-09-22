# 当前架构

`p0.py` 调用 `cli.py`；CLI 只接受固定样例。`experiments/contracts.py` 限制样例和超时；`experiments/runner.py` 为每次实验创建工作目录、复制代码快照、运行子进程、验证 metrics、收集 artifacts；`journal/store.py` 原子写入 manifest 并追加历史索引。样例只能在单次实验目录内写入结果。

当前 JSON 记录预留 `parent_id`、`hypothesis`、`plan`、`code_change`、`analysis` 等字段，支持后续接入实验树和 Agent，但 P0 不声称这些能力已经实现。将来本地和远程执行器应共用同一 run/journal 契约。P0 没有数据库或 Web 层。

P1 第一小步新增 `ideas/proposal.py` 的提案校验、`literature/sources.py` 的双来源适配器和 `literature/novelty.py` 的证据持久化。`check-novelty` 命令读取提案后逐来源检索；429 后跳过该来源的后续请求，保留查询与失败记录。原始响应与规范化候选论文并存；自动新颖性结论始终为空。该模块目前不调用 LLM，也不修改实验代码。
