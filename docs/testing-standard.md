# 验证标准

P0 代码变更后运行 `python -m unittest discover -s tests -v`。涉及 CLI 或数据格式时，再实际运行固定的 success、failure、timeout 样例并检查 `workspace/journal.jsonl` 及对应 manifest。失败和超时命令的非零退出码是预期结果。

验证包含成功指标和 artifact、失败日志、超时状态及历史读取。当前没有运行论文基准、GPU 训练、Web 构建或 LLM 联调；外部检索实际请求因 HTTP 429 未获得论文结果，不得声称这些已通过。

提案或检索逻辑变更后，同一测试命令还验证必填字段、原始响应留存、候选论文归一化和 HTTP 429 状态。需要真实集成证据时运行 `python p0.py check-novelty examples/proposal_2d_diffusion.json`，记录每个 API 的实际 HTTP 结果；不能把离线替身通过称为真实 API 成功。
