# 执行计划

| 阶段 | 范围 | 状态 | 验证 |
| --- | --- | --- | --- |
| P0-1 | 固定 CPU 样例的执行、指标、日志、artifact 和历史 | 已实现 | 三个单元验证及三个 CLI 样例实际运行 |
| P1-1 | 结构化提案输入、Semantic Scholar/OpenAlex 检索与证据保存 | 已实现；真实检索受限流影响 | 离线契约验证；本地实际调用返回 429 并正确标记证据不足 |
| P1-2 | 固定官方 2D Diffusion baseline，远端原样复现，成功后设计最薄输出 adapter | 进行中；upstream/依赖已固定，服务器新一次 SSH 检查超时 | 见 `reproduction-ai-scientist-2d-diffusion.md`；训练尚未运行 |
| P1 后续 | LLM 生成想法、真实文献核对、受限改代码与排错 | 待做 | 见 `../PROJECT_PLAN.md` |
| P2–P6 | 实验树、论文、Web、恢复与完整平台 | 规划中 | 见 `../PROJECT_PLAN.md` |

用户已确认 P1-2 复现官方 2D Diffusion baseline。代码、许可、数据、输入输出和指标已核实；下一步恢复 `labtmx56` 连接并完成只读资源检查，确认 GPU 空闲后配置环境和原样运行。输出 adapter 必须等 baseline 跑通后再实现。
