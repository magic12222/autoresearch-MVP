# 端到端 AI 科研智能体平台

当前完成 **P0：最小实验执行记录**，并开始 **P1：结构化提案与检索证据**。尚无 LLM 自动生成想法、自动改代码、实验树、论文写作或网页。总体范围见 [PROJECT_PLAN.md](PROJECT_PLAN.md)。

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

## 提案与论文检索

`examples/proposal_2d_diffusion.json` 是为后续小型 2D Diffusion 基线准备的**待验证示例假设**，不是新颖性结论或实验结果。检查命令：

```powershell
python p0.py check-novelty examples/proposal_2d_diffusion.json
```

程序会查询 Semantic Scholar 与 OpenAlex，每个来源最多取 5 条，保存提案快照、原始 API 响应、来源/查询/时间/候选论文和错误到 `workspace/novelty_checks/<check_id>/`。所有请求成功时状态是 `needs_review`，仍须人工核对候选论文；任一来源失败时状态是 `insufficient_evidence`，命令返回 2。当前本地调用两个 API 均遇到 HTTP 429，已如实记录，**没有得出新颖性判断**。如有 Semantic Scholar API key，可通过进程环境变量 `S2_API_KEY` 提供；不要写入项目文件。

## 当前限制

实验执行器只接受三个固定样例。自动生成提案、自动改代码、任意代码的隔离执行、远程服务器训练、崩溃恢复与多用户并发均未实现。服务器 `labtmx56` 的 GPU 已检查到，但本阶段没有在服务器安装或运行任务。
