# AI Task Logger (跨平台任务记录工具)

这是一个专为 AI 开发设计的**实时任务记录工具**。它能够自动记录你在使用各种 AI 助手（如 Gemini, Claude, Cursor 等）时的任务标题、Prompt、产出总结，并按日期归档。

## 🌟 核心价值
- **透明度**: 清晰追踪 AI 处理了哪些任务、修改了哪些文件。
- **追溯性**: 通过记录原始 Prompt 和最终结果，方便后续查阅和知识复用。
- **跨平台**: 无论是作为 Gemini 的技能使用，还是集成到 Claude/Cursor 的 MCP Server，甚至在命令行直接调用，都能保持统一的日志记录。

## 📦 包含内容
- **scripts/**: 核心 Python 脚本逻辑。
- **skills/**: Gemini 专用的技能描述文件 (`SKILL.md`)。
- **install.sh**: 一键安装并配置环境的脚本。

## 🚀 安装步骤
只需在终端中运行以下命令：
```bash
bash install.sh
```
安装脚本将：
1. 创建脚本安装目录（默认为 `~/scripts/ai_task_logger`）。
2. 将工具部署到 Gemini 的技能目录中。
3. 动态配置所有路径，确保一键可用。

## 🤖 使用方法

### 1. 在 Gemini 中自动使用
安装后，当 Gemini 接收到需要记录任务的指令（或主动检测到复杂任务）时，它会自动调用该工具：
- **开始任务**: Gemini 自动运行 `start` 命令并记录 Prompt。
- **结束任务**: 任务完成后，Gemini 记录产出总结。

### 2. 在 Claude / Cursor (MCP) 中使用
该工具支持 **MCP (Model Context Protocol)**。
如果你在 Cursor 或 Claude Desktop 中使用，可以将以下配置添加到 MCP 设置中：
```json
"ai-task-logger": {
  "command": "python3",
  "args": ["/你的脚本安装目录/mcp_server.py"],
  "env": {
    "WORK_LOG_ROOT": "/你的日志根目录"
  }
}
```

### 3. 手动调用 (Bash)
在处理关键任务前，你也可以手动调用：
```bash
# 开始记录
python3 ai_task_logger.py start --task-name "修复登录Bug" --prompt "用户的Prompt内容" --model "Gemini 1.5 Pro" --user "Gemini-dewei-ding"

# 结束记录
python3 ai_task_logger.py end --task-id "获取到的TASK_ID" --output "已修复 Login.java 中的 NullPointerException"
```

## ⚙️ 配置说明
默认日志保存路径为 `~/work_logs`。
如果你想修改保存位置，请在 `~/.bashrc` 或 `~/.zshrc` 中添加：
```bash
export WORK_LOG_ROOT="/your/custom/log/path"
```

---
*Created by AI for Developers.*
