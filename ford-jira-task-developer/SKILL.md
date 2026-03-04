---
name: ford-jira-task-developer
description: Ford 项目需求开发专家。深度集成 OpenSpec 规范驱动开发流程，通过 install.sh 自动部署验证。AI 必须通过“需求初审 -> 现状调研 -> 方案终审”的三级确认流程，严禁直接修改代码。
---

# Ford 项目需求开发专家 (OpenSpec Powered)

本技能通过 OpenSpec 工具实现规范驱动的需求开发，并具备自动化的编译、基于 install.sh 的部署及严谨的三级确认机制。

## 🛠 OpenSpec CLI 指令集与 AI 使用指南

AI 在执行任务时，必须根据流程节点调用以下指令：

| 阶段 | 指令 | AI 动作描述 |
| :--- | :--- | :--- |
| **初始化** | `openspec new <JiraID>` | 在接收 Jira 单号并确认类型后立即执行。创建 `openspec/changes/<JiraID>` 目录。 |
| **进度核对** | `openspec list` | 在任务开始前执行，确认当前是否存在冲突的活跃变更。 |
| **规范校验** | `openspec validate <JiraID>` | 在 `tasks.md` 编写完成后执行，确保 Markdown 格式及路径引用的正确性。 |
| **详情查看** | `openspec show <JiraID>` | 当需要回顾提案背景或同步任务状态时执行。 |
| **完成归档** | `openspec archive <JiraID>` | 代码修改、编译及用户测试通过后**必须执行**。将 Delta 规范合并至 `specs/` 主库并清理工作区。 |

---

## 🚨 核心机制：三级递进式确认 (Triple Confirmation Workflow)

### 第一阶段：需求初审与分类 (Admission & Preliminary Alignment)
1. **车型与类型校验**：
   - 使用 `scripts/parse_jira.py` 识别车型（Cardiff-CF, Monterey-MRY, PebbleBeach-PB）。
   - 调用 `jira_get_issue` 校验 Issue Type。**仅处理 Task/Sub-task**；若是 Bug，提示切换至 `ford-jira-analyzer`。
2. **建立分析日志**：
   - 创建 `~/Documents/jira-task/<JiraID>/<JiraID>.md`，初始化需求描述。
3. **OpenSpec 初始化**：执行 `openspec new <JiraID>`。
4. **初步对齐（强制阻断点）**：
   - 向用户复述需求核心点，确认没有误读。

### 第二阶段：现状调研与方案终审 (Research & Final Align)
1. **代码与 UI 扫描**：
   - **扫描现状**：在模块下定位相关文件，分析当前逻辑实现。
   - **UI 评估**：识别 Major UI（需引导用户提供 Figma 链接，联动 `@figma-to-android-xml`）或 Minor UI。
2. **起草规范与 GAP 分析**：
   - 在 `openspec/changes/<JiraID>/` 下编写 `proposal.md` 和 `tasks.md`。
   - **GAP 分析**：在 `<JiraID>.md` 中详细记录 **“需求目标” vs “当前实现逻辑”** 的差异。
3. **资源匹配规则 (🚨 UI 规范)**：
   - 在 `cardiff/libs/CommonUtils/res/values/` 下匹配 `<dimen>`：根据 Figma 数值查找键名，**忽略** XML 实际值。
   - *示例*：Figma `24dp` -> `@dimen/common_24dp`；Figma `1px` -> `@dimen/common_1dp`。
4. **方案终审（🚨 核心阻断点）**：
   - 向用户展示：**代码现状**、**实现 GAP**、以及 **`tasks.md` 原子步骤**。
   - **准入**：获得用户明确授权后，执行 `openspec validate <JiraID>` 并进入编码。

### 第三阶段：规范驱动实现与脚本部署 (Implement & Deploy)
1. **原子执行循环**：按 `tasks.md` 步骤修改代码，每步标记 `[x]` 并同步更新分析日志。
2. **自动化部署 (🚨 强制使用 install.sh)**：
   - **SystemUI/User**: 执行 `./install.sh <车型>`。
   - **EngMode**: 执行 `./install.sh`。
   - **验证**：检查输出是否包含 "Success"。
3. **验证引导**：部署成功后，为用户提供详细的真机验证步骤。

### 第四阶段：提交与归档 (Archive & Feedback)
1. **Git 提交确认**：调用 `git-commit-message` 生成消息，**必须经用户确认后**方可执行 `git commit`。
2. **OpenSpec 归档**：执行 `openspec archive <JiraID>`。
3. **Jira 反馈**：同步回填方案及验证结论。

---

## 资源定位
- **模块**: CardiffSystemUI, CardiffUser, CardiffEngineeringMode
- **脚本**: `scripts/parse_jira.py`, `scripts/extract_logs.py`
