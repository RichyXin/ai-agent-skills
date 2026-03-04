#!/usr/bin/env python3
import sys
import json
import subprocess
import os

def send_response(response):
    print(json.dumps(response))
    sys.stdout.flush()

def handle_request(req):
    req_type = req.get("type")
    
    if req_type == "initialize":
        send_response({
            "type": "initialize_response",
            "serverInfo": {
                "name": "ai-task-logger",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        })
    elif req_type == "tools/list":
        send_response({
            "type": "tools/list_response",
            "tools": [
                {
                    "name": "record_task_start",
                    "description": "Start recording a new AI task in real-time. MUST be called before starting to work on a user's prompt.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "A short, concise title for the task."
                            },
                            "prompt": {
                                "type": "string",
                                "description": "The exact user prompt or instruction."
                            },
                            "project": {
                                "type": "string",
                                "description": "The name of the current project or workspace context."
                            }
                        },
                        "required": ["task_name", "prompt", "project"]
                    }
                },
                {
                    "name": "record_task_end",
                    "description": "End the task recording and append the summary of what was done. MUST be called after the task is fully completed.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The Task ID returned by record_task_start."
                            },
                            "output": {
                                "type": "string",
                                "description": "A detailed summary of what was changed, fixed, or generated."
                            }
                        },
                        "required": ["task_id", "output"]
                    }
                }
            ]
        })
    elif req_type == "tools/call":
        tool_name = req.get("name")
        args = req.get("arguments", {})
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cli_path = os.path.join(script_dir, "ai_task_logger.py")
        
        if tool_name == "record_task_start":
            task_name = args.get("task_name", "")
            prompt = args.get("prompt", "")
            project = args.get("project", "")
            
            cmd = [sys.executable, cli_path, "start", "--task-name", task_name, "--prompt", prompt, "--project", project, "--agent", "MCP-Agent"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                task_id = output.split("TASK_ID:")[-1].strip() if "TASK_ID:" in output else output
                send_response({
                    "type": "tools/call_response",
                    "content": [{"type": "text", "text": f"Task started successfully. Task ID: {task_id}"}]
                })
            else:
                send_response({
                    "type": "tools/call_response",
                    "isError": True,
                    "content": [{"type": "text", "text": f"Failed to start task: {result.stderr}"}]
                })
                
        elif tool_name == "record_task_end":
            task_id = args.get("task_id", "")
            output_text = args.get("output", "")
            
            cmd = [sys.executable, cli_path, "end", "--task-id", task_id, "--output", output_text]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                send_response({
                    "type": "tools/call_response",
                    "content": [{"type": "text", "text": "Task ended successfully. Summary recorded."}]
                })
            else:
                send_response({
                    "type": "tools/call_response",
                    "isError": True,
                    "content": [{"type": "text", "text": f"Failed to end task: {result.stderr}"}]
                })
        else:
            send_response({
                "type": "tools/call_response",
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
            })

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            handle_request(req)
        except json.JSONDecodeError:
            pass

if __name__ == "__main__":
    main()
