#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import traceback
import tempfile
import shutil
from datetime import datetime

def main():
    # Ping log to verify execution
    with open("/tmp/hook_ping.log", "a") as f:
        f.write(f"[{datetime.now()}] Hook started\n")
        
    try:
        # BeforeAgent MUST return a JSON object to stdout
        payload_str = sys.stdin.read()
        
        if not payload_str:
            print("{}")
            return
            
        payload = json.loads(payload_str)
        event_name = payload.get('hook_event_name', 'unknown')
        session_id = payload.get('session_id', 'global')
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logger_script = os.path.join(script_dir, "ai_task_logger.py")
        task_id_file = f"/tmp/ai_task_logger_{session_id}.id"
        
        py_path = "/usr/bin/python3"
        
        if event_name == 'BeforeAgent':
            prompt = payload.get('prompt', '')
            if prompt:
                if "The following is an ephemeral message" in prompt:
                    prompt = prompt.split("The following is an ephemeral message")[0].strip()
                if "<EPHEMERAL_MESSAGE>" in prompt:
                    prompt = prompt.split("<EPHEMERAL_MESSAGE>")[0].strip()
                
                if prompt.strip():
                    task_name = prompt.split('\n')[0][:30] + ("..." if len(prompt) > 30 else "")
                    
                    # Start the task
                    cmd = [py_path, logger_script, "start", "--task-name", task_name, "--prompt", prompt, "--project", os.path.basename(os.getcwd())]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        output = result.stdout.strip()
                        task_id = output.split("TASK_ID:")[-1].strip() if "TASK_ID:" in output else None
                        if task_id:
                            with open(task_id_file, "w") as f:
                                f.write(task_id)

            print("{}")
            sys.stdout.flush()

        elif event_name == 'AfterAgent':
            response = payload.get('prompt_response', '')
            if response and os.path.exists(task_id_file):
                with open(task_id_file, "r") as f:
                    task_id = f.read().strip()
                
                summarizer_script = os.path.join(script_dir, "async_summarize.py")
                fd, temp_resp_path = tempfile.mkstemp(suffix=".txt", prefix="ai_resp_")
                with os.fdopen(fd, 'w') as f_out:
                    f_out.write(response)
                    
                env = os.environ.copy()
                env["IGNORE_WORK_LOGGER"] = "1"
                
                args = [py_path, summarizer_script, task_id, temp_resp_path, logger_script]
                subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL, start_new_session=True)

            print("{}")
            sys.stdout.flush()

    except Exception as e:
        with open("/tmp/hook_error.log", "a") as f:
            f.write(f"[{datetime.now()}] Error: {traceback.format_exc()}\n")
        print("{}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
