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

## 核心工作流 (强制要求)

在处理任何涉及修改代码、深入分析等复杂任务时，**必须**严格遵循以下“两步走”记录法：

### 第一步：实时记录任务开始 (Start)
当你明确了用户的需求和要执行的任务后，在执行任何实际操作（修改文件、分析日志等）之前，**立刻**调用以下 Bash 命令记录任务的开始。

```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py start --task-name "简短的任务标题" --prompt "用户的原始完整Prompt" --project "当前项目的工程名" --model "你当前使用的模型名(如Gemini 1.5 Pro)" --user "你的身份标识(如Gemini-dewei-ding)"
```
*执行成功后，你会得到一个 `TASK_ID`。你必须在上下文中记住这个 ID。*

### 第二步：任务完成后记录产出总结 (End)
当你完成了所有修改、代码提交、或者分析并输出结果给用户之后，调用以下命令记录最终的产出。

```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py end --task-id "第一步获取的TASK_ID" --output "简明扼要地总结你做了什么（修改了哪些文件、解决了什么Bug等）"
### 第三步（新增）：直接记录已完成的任务 (Record)
当你需要记录一个已经完成的任务（例如任务已经开始但忘记记录，或者想一次性记录完整信息）时，使用 `record` 命令。

```bash
python3 /home/rentianxin/.config/opencode/mega-tools/ai_task_logger/ai_task_logger.py record --task-name "字符串资源整理" --prompt "用户的原始完整Prompt" --output "任务完成总结..." --project "CardiffSystemUI" --model "Claude" --user "rentianxin" --task-id "ses_352611a33ffeou6aMvroKwbcDx"
```
*注意：`--task-id` 是可选的，如果不提供会自动生成。可以使用session ID作为task-id。*



## MCP 集成说明
对于 Claude 或 Codex/Cursor，可以通过 MCP Server 集成该工具：
MCP Server 路径: `/home/rentianxin/.config/opencode/mega-tools/ai_task_logger/mcp_server.py`
使用工具: `record_task_start` 和 `record_task_end`
