---
name: openspec-manager
description: 这是一个专门为 AI 助手设计的 OpenSpec 流程管理器。它通过规范驱动开发（SDD）强制执行从提案到归档的结构化生命周期，确保 AI 开发过程中的上下文一致性和确定性。适用于所有需求开发、Bug 修复和系统重构。
---

# OpenSpec 管理器 (AI 专用指南)

该技能定义了 AI 助手在执行任何代码变更时必须遵循的 OpenSpec 标准流程。它通过将“做什么”与“怎么做”在物理文件上进行隔离，防止上下文丢失。

## AI 核心指令：遵循 OpenSpec 的原则
1. **先规后码 (Specs Before Code)**：严禁在没有完成 `proposal`、`specs` 和 `tasks` 之前修改任何源代码（除非是为了调研而进行的临时探索）。
2. **文档即事实 (Artifacts as Truth)**：所有的开发逻辑、设计决策和任务清单必须持久化在 `.openspec/` 目录下的 Markdown 文件中。
3. **闭环管理**：每个任务必须以 `openspec archive` 结束，将变更合并到系统的主规范中。

## AI 详细操作规程

### 1. 启动变更 (New Change)
当接收到新需求或 Bug 修复任务时：
- 执行 `openspec new change [change-name]`（使用 kebab-case）。
- 执行 `openspec instructions proposal --change [change-name]`。
- **AI 动作**：解析上述指令输出的 `<instruction>` 和 `<template>`，结合当前任务上下文，编写并保存 `proposal.md`。

### 2. 定义规范 (Define Specs)
在提案被确认后：
- 执行 `openspec instructions specs --change [change-name]`。
- **AI 动作**：读取提案中的 `Capabilities`，在 `openspec/changes/[name]/specs/[capability]/spec.md` 中编写具体需求。
- **强制格式**：必须使用 `#### Scenario: [描述]` (4个#) 定义验收场景，并使用 WHEN/THEN 格式。

### 3. 技术设计与任务分解 (Design & Tasks)
- 依次执行 `openspec instructions design` 和 `openspec instructions tasks`。
- **AI 动作**：根据规范生成技术实现方案和具体的待办清单 (`tasks.md`)。

### 4. 自动化实现 (Apply)
- 执行 `openspec apply --change [change-name]`。
- 或者 AI 根据 `tasks.md` 手动逐项修改代码。
- **验证**：每次修改后，AI 必须运行相关测试或编译命令。

### 5. 完成并归档 (Archive)
- 执行 `openspec archive [change-name]`。
- 此操作会自动将 `changes/` 目录下的增量规范同步到 `openspec/specs/` 主目录下。

## AI 常用查询指令
- `openspec list`: 获取当前所有的活跃变更。
- `openspec status --change [name]`: 获取当前变更的进度（哪些 artifact 已完成，哪些被阻塞）。
- `openspec show [name]`: 查看某个变更的完整内容。

## 故障排除
- 如果命令执行失败并提示 `Missing required option --change`，说明需要显式指定变更名称。
- 如果 `archive` 失败，通常是因为 `specs` 文件的格式（如 Scenario 的 # 数量）不正确。
