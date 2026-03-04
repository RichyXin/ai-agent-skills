---
name: prompt-to-command
description: Converts text prompts or files into executable OpenCode slash commands.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: command-creation
---

# Prompt to Command Converter

## Professional Context
I am a specialized skill designed to encapsulate user-provided prompts (text or files) into OpenCode's executable Slash Command format. This allows users to easily reuse their favorite prompts as quick commands.

## Core Capabilities

### Input Analysis
- **Source Detection**: Determines if the input is a file path or raw text.
- **Name Extraction**: Identifies the desired command name (e.g., from "/refactor" -> "refactor").
- **Description Generation**: Creates a brief description for the command metadata based on content.

### Command Construction
- **Format Standardization**: Wraps content in the required Markdown frontmatter structure.
- **Argument Handling**: Automatically appends the user input handling block (`用户输入：$user_message`).
- **File Management**: Writes the resulting file to the correct `command/` directory.

## Command Format Specification
The generated commands follow this structure:

```markdown
---
description: <brief_description>
---

<prompt_content>

用户输入：
$user_message
```

## Usage Workflow

1.  **Trigger**: User asks to "make a command" or "turn this prompt into a command".
2.  **Process**:
    *   If a file path is provided, I read it.
    *   If raw text is provided, I use it directly.
3.  **Create**: I write a new `.md` file in `~/.config/opencode/command/`.
4.  **Verify**: I confirm the file creation.

## Example Interaction
**User**: "Turn `my_prompt.txt` into a command called `fix-bug`."
**Action**:
1. Read `my_prompt.txt`.
2. Write to `~/.config/opencode/command/fix-bug.md`.
3. Notify user of success.
