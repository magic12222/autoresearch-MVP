# 项目协作规则

开始工作前阅读 `handoff.md`、`dev-log/todo.md` 和相关的 `docs/` 文件。`PROJECT_PLAN.md` 是分阶段规划；已确认的当前实现范围以 `docs/requirements.md` 和 `docs/execution-plan.md` 为准。发生范围或架构变化时先更新对应文档。

本项目的源码与持久项目文件只保存在此 Windows 项目目录。`labtmx56` 是后续训练的远程执行资源，当前不在服务器建立第二份项目源仓库。P0 仅运行 `examples/` 中固定样例，不允许将 CLI 改成任意命令执行入口。不得把凭据写入源码、日志、文档或 Git。

本地入口：`python p0.py run success`、`python p0.py list`。验证：`python -m unittest discover -s tests -v`。行为、验收或恢复信息变化时更新 `dev-log/progress.md`、`dev-log/todo.md` 与 `handoff.md`；重大决策记入 `dev-log/decisions.md`。
