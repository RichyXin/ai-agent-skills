---
name: ai-task-logger
description: 跨模型、跨平台的AI任务实时记录工具。在开始处理用户需求前，记录任务和Prompt；在处理完成后，记录产出总结。
triggers:
  - 记录任务
  - 开始记录
  - 任务日志
allowed-tools:
  - Bash
  - Read
  - Write
---

# AI Task Logger (跨平台任务记录器)

这是一个统一的跨模型、跨平台任务记录工具，用于实时记录你接收到的 Prompt 以及你最终的产出。

## ⚠️ OpenCode 专用工作流 (重要)

在 OpenCode 中，由于无法保持 task_id 的上下文状态，**必须使用 `record` 命令一次性记录完整任务**。

### OpenCode 使用方法

任务完成后，使用 `session_id` 作为 `task_id`，一次性记录：

```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py record \
  --task-name "简短的任务标题" \
  --prompt "用户的原始完整Prompt" \
  --output "任务完成总结（修改了哪些文件、解决了什么问题）" \
  --project "项目名称" \
  --agent "模型名称(如GLM-5)" \
  --source "OpenCode" \
  --task-id "ses_xxx"  # 使用当前会话的 session_id
```

**参数说明**：
- `--source "OpenCode"`: 标注任务来源为 OpenCode 平台（必填）
- `--task-id`: 使用当前会话的 session_id（格式：`ses_xxx`）

### 如何获取 session_id

在 OpenCode 中，session_id 是当前会话的唯一标识，格式为 `ses_xxx`。你可以在对话开始时看到它，或者从系统提示中获取。

---

## Gemini 专用工作流 (两步走)

在 Gemini 中，可以使用 hook 自动触发，或手动执行两步走：

### 第一步：记录任务开始
```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py start --task-name "任务标题" --prompt "用户的Prompt" --project "项目名" --agent "Gemini"
```

### 第二步：记录产出总结
```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py end --task-id "获取的TASK_ID" --output "产出总结"
```

---

## MCP 集成说明

对于 Claude 或 Codex/Cursor，可以通过 MCP Server 集成该工具：
- MCP Server 路径: `/home/rentianxin/.config/opencode/mega-tools/ai_task_logger/mcp_server.py`
- 使用工具: `record_task_start` 和 `record_task_end`

---

## 日志格式示例

```markdown
### [14:30:25] [GLM-5[OpenCode]] [CardiffSystemUI] 任务: 修复字符串资源冲突 <!-- TASK_ID: ses_abc123 -->
- **Prompt**:
    用户的原始 Prompt 内容
- **主要产出**: 
    修改了 strings.xml，解决了资源冲突问题
----------------------------------------
```

**来源标注说明**：
- `[GLM-5]` - 无来源标注，可能是 Gemini 或其他平台
- `[GLM-5[OpenCode]]` - 明确标注来自 OpenCode 平台