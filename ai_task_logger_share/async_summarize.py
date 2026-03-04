#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import shutil
import json
from datetime import datetime

def main():
    if len(sys.argv) < 4:
        return
        
    task_id = sys.argv[1]
    temp_resp_path = sys.argv[2]
    logger_script = sys.argv[3]
    debug_log = "/tmp/ai_task_logger_hook_debug.log"
    
    if not os.path.exists(temp_resp_path):
        return
        
    try:
        with open(temp_resp_path, 'r', encoding='utf-8', errors='ignore') as f:
            response = f.read()
            
        prompt = f"""请作为工作日志助手，简明扼要地总结下面这段AI的回复内容。
你的总结将被记录为任务的“主要产出”。
要求：
1. 不要输出任何废话或前缀（例如“好的”、“总结如下”等）。
2. 直接输出核心产出：修改了哪些文件、做了什么分析、输出了什么代码，或者报错原因。
3. 尽量控制在100字以内，保持专业严谨。

待总结的AI回复内容如下（可能被截断）：
{response[:2000]}
"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp:
            temp.write(prompt)
            temp_path = temp.name

        env = os.environ.copy()
        env["IGNORE_WORK_LOGGER"] = "1"
        
        gemini_path = shutil.which("gemini")
        if not gemini_path:
            gemini_path = "gemini"
            
        cmd = f"{gemini_path} --no-hooks -p 'Summarize the provided content as requested.' < {temp_path}"
        result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
        
        os.unlink(temp_path)
        
        if result.returncode == 0 and result.stdout.strip():
            clean_lines = []
            for line in result.stdout.splitlines():
                if any(marker in line for marker in [
                    "Created execution plan", 
                    "Expanding hook command", 
                    "Hook execution",
                    "Hook Triggered",
                    "Processing piped text",
                    "Deduplicated hook",
                    "[AI Thinking...]"
                ]):
                    continue
                clean_lines.append(line)
                
            output_summary = "\n".join(clean_lines).strip()
            if not output_summary:
                output_summary = "任务已执行。"
        else:
            output_summary = f"完成。摘要预览: {response[-100:].strip()}"
            
        # Call logger script end command
        cmd_end = ["python3", logger_script, "end", "--task-id", task_id, "--output", output_summary]
        subprocess.run(cmd_end, env=env)

    except Exception as e:
        import traceback
        with open(debug_log, "a") as f:
            f.write(f"[{datetime.now()}] Async Summarize Exception:\n{traceback.format_exc()}\n")
    finally:
        if temp_resp_path and os.path.exists(temp_resp_path):
            try:
                os.unlink(temp_resp_path)
            except:
                pass

if __name__ == "__main__":
    main()
