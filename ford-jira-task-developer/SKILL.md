---
name: ford-jira-task-developer
description: Ford 项目需求开发专家。深度集成 OpenSpec 规范驱动流程，支持全量变更扫描与自动部署验证。AI 必须严格遵循“五级确认”流程，并维护高度结构化的本地分析日志，严禁删除任何既有规则。
---

# Ford 项目需求开发专家 (OpenSpec Powered)

本技能旨在通过 OpenSpec 工具、严谨的多级确认机制以及标准化的“开发记录手册”，确保需求实现的高质量、透明度与可追溯性。

## 🛠 OpenSpec CLI 指令集与 AI 交互标准

AI 必须根据流程节点调用以下指令，严禁跳步：

| 阶段 | 指令 | AI 动作描述 |
| :--- | :--- | :--- |
| **初始化** | `openspec new change <JiraID小写>` | 确认 Task 类型后执行。创建 `openspec/changes/<jira-id>` 目录。 |
| **进度核对** | `openspec list` | 任务开始前执行，确认当前是否存在冲突的活跃变更。 |
| **规范校验** | `openspec validate <jira-id>` | 在 `tasks.md` 编写后执行，确保格式及路径引用正确。 |
| **详情查看** | `openspec show <jira-id>` | 当需要回顾提案背景或同步任务状态时执行。 |
| **完成归档** | `openspec archive <jira-id>` | 测试通过后**必须执行**。合并规范至主库并清理工作区。 |

---

## 🚨 核心准则 (Core Mandates - 必须全部遵守)

1. **规范先行 (Spec-First)**：严禁跳过 OpenSpec 规范阶段直接修改代码。
2. **三级递进式确认 (Triple Align)**：正式编码前必须经过：[需求初审] -> [现状调研与 GAP 分析] -> [方案终审]。
3. **全量变更扫描 (Whole Workspace Scan)**：在代码审核阶段，AI 必须执行 `git status` 及 `git diff` 扫描 **AI 逻辑 + 用户手动修改** 的全量变动。
4. **资源匹配规则 (UI/Dimen Standard)**：在 `cardiff/libs/CommonUtils/` 下匹配尺寸：**按 Figma 数值查找键名，忽略 XML 实际值**（如 Figma `24dp` -> `@dimen/common_24dp`）。对于大范围 UI 修改，需引导用户提供 Figma 链接并联动 `@figma-to-android-xml`。
5. **脚本化部署 (Scripted Deploy)**：强制通过模块根目录下的 `install.sh` 进行编译安装。**SystemUI/User**: `./install.sh <车型(cardiff/monterey)>`；**EngMode**: `./install.sh`。禁止直接手动执行 `adb push`。
6. **自动验证 (Auto-Verify)**：必须确认脚本输出包含 "Success" 关键字后，方可引导用户验证。
7. **提交强管控 (Commit Control)**：生成提交记录时，必须调用 `git-commit-message` 并展示给用户，**经批准后**方可执行 Git 提交。
8. **本地化逻辑原则 (Locality)**：业务逻辑代码（如版本检测工具类等专属业务）应放在对应 App 模块下，严禁随意放入公共库中。
9. **不删减原则 (Append Only)**：AI 在更新本技能文档时，仅允许增量叠加规则，严禁删除、覆盖或精简任何已存在的规则。

---

## 🛠 分析日志规范 (Analysis Log Standard - 🚨 强制执行)

AI 必须在 `~/Documents/jira-task/<JiraID>/<JiraID>.md` 中维护详实日志，排版必须美观，内容必须详实。每次进入新阶段时**必须**实时更新，严禁事后补录。

### 模板结构 (Template)
- **# [JiraID]: [标题]**
- **## 1. 需求解析 (Requirement Analysis)**
  - 背景描述、核心功能点、验收标准。
- **## 2. 现状调研 (Technical Research)**
  - 受影响文件清单、当前逻辑链路分析、调研发现的坑点。
- **## 3. 实现方案与 GAP 分析 (Strategy & Gap)**
  - 核心逻辑变更方案、数据存储/协议变动、实现目标与现状的 GAP。
- **## 4. 任务执行记录 (Execution Log)**
  - 关联 OpenSpec `tasks.md` 的进度，记录编译错误及修复过程。
- **## 5. 验证与交付 (Verification & Delivery)**
  - 真机测试反馈记录、Git 提交信息快照、归档状态。

---

## 🛠 核心工作流 (Execution Workflow)

### 第一阶段：需求准入与初步对齐 (Admission)
1. **车型与类型识别**：使用 `scripts/parse_jira.py` 识别车型（Cardiff-CF, Monterey-MRY, PebbleBeach-PB）。调用 `jira_get_issue` 校验。仅处理 `Task`，若是 `Bug` 则提示切换至 `ford-jira-analyzer` 技能。
2. **初始化日志**：创建目录及日志文件，按上述模板写入第一章节。
3. **OpenSpec 初始化**：执行 `openspec new change <JiraID小写>`。
4. **需求初审（强制阻断点）**：向用户复述需求核心点，获得“理解无误”的确认后方可继续。

### 第二阶段：现状调研与方案终审 (Research & Final Align)
1. **深度扫描**：扫描现状代码，分析当前逻辑实现。结合需求判断 UI 修改范围。
2. **起草规范与 GAP 分析**：在 `openspec/changes/<JiraID小写>/` 下编写 `proposal.md` 和 `tasks.md`。在分析日志中记录“现状 vs 目标”的 GAP。
3. **方案终审（强制阻断点）**：向用户展示代码现状、GAP 分析及 `tasks.md` 原子步骤。获得明确批准后，执行 `openspec validate <JiraID小写>` 并进入编码阶段。

### 第三阶段：规范驱动实现与脚本部署 (Implement & Deploy)
1. **原子执行**：严格按照 `tasks.md` 步骤修改代码，每步完成标记 `[x]` 并同步更新分析日志进度。
2. **自动化部署 (🚨 强制 install.sh)**：
   - **SystemUI/User**: `./install.sh <车型(cardiff/monterey)>`。
   - **EngMode**: `./install.sh`。
   - **验证**：检查输出是否包含 "Success"。
3. **测试引导**：部署成功后，为用户提供详细的真机验证步骤。

### 第四阶段：全量代码审核 (Comprehensive Review - 🚨 强制阻断)
1. **前提**：用户反馈真机测试通过。
2. **同步全量变更**：**必须**执行 `git status` 及 `git diff` 扫描工作空间内 **AI 开发逻辑 + 用户手动修改（UI/资源/文案）** 的所有变动。
3. **交互**：列出包含双方贡献的完整文件清单及变更点摘要，并提示用户进行最后一次全量代码审核。

### 第五阶段：提交与归档 (Commit & Archive)
1. **Git 确认**：调用 `git-commit-message` 技能生成规范消息，经用户最终批准后执行 `git commit`。
2. **归档**：执行 `openspec archive <JiraID小写>`。
3. **Jira 回填**：同步回填实现方案及验证结论到 Jira Comment，并完成分析日志的最终登记。

---

## 资源定位
- **工作模块**: `/home/rentianxin/Code/JMC/cardiff/CardiffSystemUI`, `/home/rentianxin/Code/JMC/cardiff/CardiffUser/`, `/home/rentianxin/Code/JMC/cardiff/CardiffEngineeringMode/`
- **辅助脚本**: `scripts/parse_jira.py`, `scripts/extract_logs.py`, `scripts/extract_pid.py`
