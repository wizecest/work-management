# Work Management · 工作管理助理

把项目资料和工作记录整理成今天能做的事、看得懂的总结，以及有依据的台账。

这是一个供 Agent 使用的中文技能包，适合同时跟进多个项目的人。它提炼自实际工程项目管理工作流，公开版使用虚构示例，不含原工作空间的数据和运行服务。

## 能做什么

| 场景 | 得到什么 | 示例请求 |
| --- | --- | --- |
| 今日安排 | 项目概览、具体动作、到期事项、需要协调或决策的事 | 帮我看看今天先做什么 |
| 工作记录 | 带日期、项目归属和来源的日志 | 记一下，示例项目甲今天收到修改稿 |
| 日/周/月/季/年总结 | 成果、承诺兑现、问题、风险变化、下一阶段重点 | 整理本周工作 |
| 管理层审视 | 全部项目检查、异常分析、干预效果、升级事项 | 从管理层看一下全部项目 |
| 对外台账 | 项目时间线、问题、措施和下一步计划 | 按台账口径整理项目进展 |
| 补同步与复盘 | 待同步清单、事实时间线和经确认的经验 | 检查最近三天是否漏记 |

## 两分钟试用

1. 让你的 Agent 读取 [SKILL.md](skills/work-management/SKILL.md)。
2. 提供 [虚构资料](examples/demo-input.md)。
3. 发送以下请求：

```text
使用 work-management，按示例中的 2026-04-08 作为盘点日，整理今日安排。
只使用示例资料，不改动任何文件。保留来源和待核实事项。
```

用 [示例核对说明](examples/demo-review.md) 检查结果。示例只是行为检查材料，没有包含预先生成的模型答卷。

## 安装和日常使用

需要能够读取文件、执行技能指令的 Agent。技能本身不要求运行 Python；安装与发布检查脚本需要 Python 3.10 或以上，只使用标准库。

可以直接把 [skills/work-management](skills/work-management) 整个文件夹放进目标宿主已经确认的技能目录。也可以运行：

```text
python scripts/install_skill.py --skills-dir <目标宿主的技能目录>
```

脚本只新增 `work-management/`，目标已存在就停止，不覆盖已有技能。不要把整个仓库复制成技能目录。安装后按宿主要求重新发现技能；不确定宿主目录时，先用上述直接读取方式试用。

支持 `$work-management` 的宿主可用它显式调用；其余宿主可用自然语言请求 Agent 使用本技能。文档中的 `/today`、`/work`、`/ledger` 是工作流名称，本仓库不自动注册宿主斜杠命令。

实际使用时提供资料目录或文件，并说明项目范围、截至日期、是否保存。例如：

```text
使用 work-management，根据我指定的项目资料整理本周总结，
截至 2026-04-08，保存到我提供的成果目录；不修改项目事实。
```

## 资料如何读取

- **资料模式（默认）**：读取用户给出的记录、文件和已确认状态，标明资料截止时间。没有权威当前状态时，说明“状态待核对”；不把旧日志推断成现行节点。
- **系统适配模式（可选）**：已有 PM-Obsidian 或其他权威项目系统时，通过该系统的正式读取和事务入口工作。本包不附带原系统引擎，见 [适配约定](docs/integration.md)。

技能可以生成安排、材料和总结。事实入账、实际发消息、自动定时检查、审批节点关闭，分别依赖宿主能力、业务证据与已有授权，不能用一段生成文字冒充执行结果。

## 包含的内容

- [技能入口](skills/work-management/SKILL.md)：模式选择、证据和权限边界。
- [今日安排](skills/work-management/references/daily.md)、[周期总结](skills/work-management/references/summaries.md)、[管理层审视](skills/work-management/references/portfolio.md)、[对外台账](skills/work-management/references/ledger.md)、[日志与复盘](skills/work-management/references/records.md)：按需读取。
- [工作空间模板](skills/work-management/assets/workspace-template.md)：首次接入时明确资料、状态和保存位置。
- [使用与保存约定](docs/usage.md)、[来源与改编说明](docs/provenance.md)。

公开版没有 PM Control 界面、独立状态引擎、通知服务、自主学习功能或原仓库旧 Shell 脚本。

## 检查与打包

```text
python scripts/check_release.py
python -m unittest discover -s tests -v
python scripts/build_release.py --output-dir <压缩包保存目录>
```

发布采用显式文件清单 [release-files.json](release-files.json)。脚本检查清单、链接、明显私有路径和常见密钥格式，再只打包清单中的文件。检查范围见 [发布说明](docs/releasing.md)，它不证明业务判断或所有隐私检查都已完成。

版本：0.1.0。许可证：[MIT](LICENSE)。
