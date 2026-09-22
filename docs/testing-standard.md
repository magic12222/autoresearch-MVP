# 验证标准

P0 代码变更后运行 `python -m unittest discover -s tests -v`。涉及 CLI 或数据格式时，再实际运行固定的 success、failure、timeout 样例并检查 `workspace/journal.jsonl` 及对应 manifest。失败和超时命令的非零退出码是预期结果。

验证包含成功指标和 artifact、失败日志、超时状态及历史读取。当前没有运行论文基准、GPU 训练、Web 构建、外部检索或 LLM 联调，不得声称这些通过。
