# 当前架构

`p0.py` 调用 `cli.py`；CLI 只接受固定样例。`experiments/contracts.py` 限制样例和超时；`experiments/runner.py` 为每次实验创建工作目录、复制代码快照、运行子进程、验证 metrics、收集 artifacts；`journal/store.py` 原子写入 manifest 并追加历史索引。样例只能在单次实验目录内写入结果。

当前 JSON 记录预留 `parent_id`、`hypothesis`、`plan`、`code_change`、`analysis` 等字段，支持后续接入实验树和 Agent，但 P0 不声称这些能力已经实现。将来本地和远程执行器应共用同一 run/journal 契约。P0 没有数据库或 Web 层。
