# 决策

## P0 使用固定样例和标准库

原因：先验证实验历史和可追溯数据，再接入 LLM、任意代码和远程 GPU。固定样例将执行风险和依赖成本限制在可检查范围。后续执行器可变，但 run/journal 契约应保持可迁移。

## P1-2 以 submodule 固定官方 upstream，运行与导入分离

原因：官方 2D Diffusion baseline 应保持原样、可核验且不污染平台源码。AI-Scientist 和 NPEET 分别固定完整 commit；远端按官方命令运行，平台只在成功后通过只读 adapter 导入 JSON、日志和 artifact 元数据。这样可避免把 P0 runner 扩展为任意命令入口，也能明确遵守 AI-Scientist 的自定义许可证。
