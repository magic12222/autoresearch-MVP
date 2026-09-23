# 进展

## 2026-09-22

- 建立新项目规划 `PROJECT_PLAN.md`，核对论文与参考仓库。
- 实现 P0 固定样例执行器、实验记录和 CLI。
- 实际执行三个单元验证，均通过；实际运行成功、失败、超时三个 CLI 样例，均产生相应记录。未运行 GPU 训练。
- 用户选择小型 2D Diffusion 作为后续复现基线。新增结构化提案校验、双来源论文检索及原始证据保存；6 项单元验证通过。
- 实际检索时本地 Semantic Scholar 与 OpenAlex 均返回 HTTP 429，报告为 `insufficient_evidence`，未形成新颖性结论。服务器只读网络检查：Semantic Scholar 为 429，OpenAlex 为 200；未部署或运行平台代码。

## 2026-09-23

- 进入 P1-2，核验 SakanaAI/AI-Scientist 当前 `main` commit、限制性许可证和官方 2D Diffusion 模板结构。
- 将 AI-Scientist `1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb` 与 NPEET `8b0d9485423f74e5eb199324cf362765596538d3` 作为独立 Git submodule 固定；未修改官方实验逻辑。
- 记录官方输入、输出、指标、依赖、原样运行命令、成功条件和最薄 adapter 边界。
- 新一次 `labtmx56` SSH 连接在只读预检前超时；未在服务器创建环境、写文件或启动训练，当前 GPU/磁盘/环境状态仍待核实。
- 本地回归运行 `python -m unittest discover -s tests -v`，6 项均通过；两个 upstream submodule 工作树均干净。
