# 端到端 AI 科研智能体平台

当前完成 **P0：最小实验执行记录**。这是论文复现的第一块基础设施，还没有想法生成、文献检索、LLM 自动改代码、实验树、论文写作或网页。总体范围见 [PROJECT_PLAN.md](PROJECT_PLAN.md)。

## 环境

本地使用 Windows、Python 3.11 或更新版本；P0 无第三方运行依赖。固定样例不训练模型，不使用服务器 GPU。

## 运行

在项目根目录执行：

```powershell
python p0.py run success
python p0.py run failure
python p0.py run timeout --timeout 0.3
python p0.py list
```

失败或超时命令会返回非零退出码，这是预期行为。每次运行在 `workspace/experiments/<experiment_id>/` 留下 `manifest.json`、代码快照、stdout/stderr、可用的指标和 artifacts；`workspace/journal.jsonl` 是追加式历史索引。`workspace/` 已排除出 Git。样例的数字只用于验证记录链路，**不是科研结果**。

验证命令：

```powershell
python -m unittest discover -s tests -v
```

## 当前限制

执行器只接受三个固定样例。自动改代码、任意代码的隔离执行、远程服务器训练、崩溃恢复与多用户并发均未实现。服务器 `labtmx56` 的 GPU 已检查到，但本阶段没有在服务器安装或运行任务。
