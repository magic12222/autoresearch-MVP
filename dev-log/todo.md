# 待办

- [x] P0-1：固定 CPU 样例执行与持久记录。
- [ ] 评审 P0 输出契约和运行记录。
- [x] 选定 P1 的小型 2D Diffusion 研究基线。
- [x] 核实 2D Diffusion 模板、许可、数据、输入输出和指标；以 submodule 固定官方 upstream 与 NPEET。
- [x] 恢复 `labtmx56` 连接并核实 GPU、CUDA/Python/conda、磁盘和占用；已建立隔离环境。
- [ ] 在空闲 GPU 上原样运行官方 2D Diffusion baseline，保存完整复现证据。
- [ ] baseline 成功后实现最薄的官方输出到 ExperimentRun/journal adapter。
- [x] 建立结构化提案和检索证据的第一版接口。
- [ ] 解决至少一个论文检索源在运行环境中的 HTTP 429，核对真实候选论文。
- [ ] 核实 `labtmx56` 的资源使用规则与空闲时段；预检时四张 GPU 均有现存任务。
- [ ] 在开放生成代码前确定隔离执行方案。
