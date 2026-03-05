#!/usr/bin/env python3
import os
import sys
import argparse
import time
import re
from datetime import datetime
import hashlib
try:
    import fcntl
except ImportError:
    fcntl = None

def get_log_dir():
    # 1. Check environment variable
    base_dir = os.environ.get("WORK_LOG_ROOT")
    
    # 2. Check for hardcoded preferred path for the current user
    if not base_dir:
        preferred = "/home/dingdewei/div/AI/docs/IFS-WUHAN2/DDW"
        if os.path.exists(preferred):
            base_dir = preferred
            
    # 3. Check .bashrc as a fallback
    if not base_dir:
        try:
            bashrc_path = os.path.expanduser("~/.bashrc")
            if os.path.exists(bashrc_path):
                with open(bashrc_path, "r", encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if "WORK_LOG_ROOT" in line and "=" in line:
                            match = re.search(r'WORK_LOG_ROOT=["\']?([^"\'\s#]+)["\']?', line)
                            if match:
                                base_dir = match.group(1)
                                break
        except Exception:
            pass
    
    # 4. Fallback to default
    if not base_dir:
        base_dir = os.path.expanduser("~/work_logs")
        
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def get_file_path(date_obj):
    base_dir = get_log_dir()
    month_dir = date_obj.strftime("%Y-%m")
    file_name = date_obj.strftime("%Y-%m-%d") + ".md"
    month_path = os.path.join(base_dir, month_dir)
    os.makedirs(month_path, exist_ok=True)
    return os.path.join(month_path, file_name)

def generate_task_id():
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

def get_current_session_id():
    """获取 OpenCode session_id，用于作为 task_id"""
    import subprocess
    try:
        result = subprocess.run(["opencode", "session", "current"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def lock_file(fd):
    if fcntl: fcntl.flock(fd, fcntl.LOCK_EX)

def unlock_file(fd):
    if fcntl: fcntl.flock(fd, fcntl.LOCK_UN)

def format_prompt(prompt_text):
    lines = prompt_text.replace('\\n', '\n').splitlines()
    return "\n".join(["    " + line if line.strip() else "" for line in lines])

def cmd_start(args):
    now = datetime.now()
    task_id = generate_task_id()
    file_path = get_file_path(now)
    
    timestamp = now.strftime("%H:%M:%S")
    agent = args.agent or os.environ.get("USER", "unknown-agent")
    project = args.project or os.path.basename(os.getcwd())
    
    formatted_prompt = format_prompt(args.prompt)
    
    entry = (
        f"\n### [{timestamp}] [{agent}] [{project}] 任务: {args.task_name} <!-- TASK_ID: {task_id} -->\n"
        f"- **Prompt**:\n{formatted_prompt}\n"
        f"- **主要产出**: \n    [AI 执行中... 等待产出]\n"
        f"----------------------------------------\n"
    )
    
    fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
    try:
        lock_file(fd)
        size = os.path.getsize(file_path)
        if size > 0:
            os.lseek(fd, 0, os.SEEK_SET)
            content = os.read(fd, size).decode('utf-8', errors='ignore')
            clean_pattern = re.compile(
                r"\n### \[[^\]]+\] \[[^\]]+\] \[[^\]]+\] 任务: [^\n]+ <!-- TASK_ID: [a-f0-9]{8} -->\n"
                r"- \*\*Prompt\*\*:\n(?:    .*\n)*"
                r"- \*\*主要产出\*\*: \n    \[AI 执行中\.\.\. 等待产出\]\n"
                r"----------------------------------------\n"
            )
            content = clean_pattern.sub('', content)
            os.lseek(fd, 0, os.SEEK_SET)
            os.ftruncate(fd, 0)
            os.write(fd, content.encode('utf-8'))
            
        os.lseek(fd, 0, os.SEEK_END)
        os.write(fd, entry.encode('utf-8'))
    finally:
        unlock_file(fd)
        os.close(fd)
        
    print(f"Task Started. TASK_ID: {task_id}")
    return task_id

def cmd_end(args):
    now = datetime.now()
    found = False
    
    for i in range(7):
        date_obj = datetime.fromtimestamp(now.timestamp() - i * 86400)
        file_path = get_file_path(date_obj)
        if not os.path.exists(file_path):
            continue
            
        fd = os.open(file_path, os.O_RDWR)
        try:
            lock_file(fd)
            size = os.path.getsize(file_path)
            if size == 0:
                continue
                
            os.lseek(fd, 0, os.SEEK_SET)
            content = os.read(fd, size).decode('utf-8', errors='ignore')
            
            pattern_str = r"(### \[[^\]]+\] \[[^\]]+\] \[[^\]]+\] 任务: [^\n]+ <!-- TASK_ID: " + re.escape(args.task_id) + r" -->\n).*?(----------------------------------------\n)"
            pattern = re.compile(pattern_str, re.MULTILINE | re.DOTALL)
            
            match = pattern.search(content)
            if match:
                header = match.group(1)
                block_content = match.group(0)
                prompt_match = re.search(r"(- \*\*Prompt\*\*:\n.*?)(?=- \*\*主要产出\*\*|- \*\*状态\*\*|$)", block_content, re.DOTALL)
                prompt_str = prompt_match.group(1) if prompt_match else "- **Prompt**:\n    (未提取到内容)\n"
                formatted_output = "\n".join(["    " + line for line in args.output.replace('\\n', '\n').splitlines()])
                
                # 过滤假数据
                if "测试跨模型工具" in header or "给我写个记录工具" in prompt_str or "```markdown" in formatted_output or "无明显输出内容" in formatted_output or "待总结的AI回复内容如下" in formatted_output:
                    new_content = content[:match.start()] + content[match.end():]
                    os.lseek(fd, 0, os.SEEK_SET)
                    os.ftruncate(fd, 0)
                    os.write(fd, new_content.encode('utf-8'))
                    found = True
                    break
                    
                if not formatted_output.strip():
                    formatted_output = "    任务完成。"
                output_str = f"- **主要产出**: \n{formatted_output}\n"
                footer = match.group(2)
                new_block = header + prompt_str + output_str + footer
                new_content = content[:match.start()] + new_block + content[match.end():]
                os.lseek(fd, 0, os.SEEK_SET)
                os.ftruncate(fd, 0)
                os.write(fd, new_content.encode('utf-8'))
                found = True
                break
        finally:
            unlock_file(fd)
            os.close(fd)
            
        if found:
            break
            
    def cmd_record(args):
        """直接记录一个已完成的任务（一次性写入完整信息）"""
        now = datetime.now()
        # 使用传入的 task_id 或自动生成
        task_id = args.task_id if args.task_id else generate_task_id()
        file_path = get_file_path(now)
    
        timestamp = now.strftime("%H:%M:%S")
        agent = args.agent or os.environ.get("USER", "unknown-agent")
        project = args.project or os.path.basename(os.getcwd())
    
        # 如果有 source 参数，在 agent 中标注来源
        display_agent = agent
        if args.source:
            display_agent = f"{agent}[{args.source}]"
    
        formatted_prompt = format_prompt(args.prompt)
        formatted_output = "\n".join(["    " + line for line in args.output.replace('\\n', '\n').splitlines()])
    
        entry = (
        f"\n### [{timestamp}] [{display_agent}] [{project}] 任务: {args.task_name} <!-- TASK_ID: {task_id} -->\n"
        f"- **Prompt**:\n{formatted_prompt}\n"
        f"- **主要产出**: \n{formatted_output}\n"
        f"----------------------------------------\n"
        )
    
        fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
        try:
            lock_file(fd)
            os.lseek(fd, 0, os.SEEK_END)
            os.write(fd, entry.encode('utf-8'))
        finally:
            unlock_file(fd)
            os.close(fd)
        
        print(f"Task Recorded. TASK_ID: {task_id}")
        return task_id

def main():
    parser = argparse.ArgumentParser(description="Cross-model AI Task Logger")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_start = subparsers.add_parser("start")
    parser_start.add_argument("--task-name", required=True)
    parser_start.add_argument("--prompt", required=True)
    parser_start.add_argument("--project", default="")
    parser_start.add_argument("--agent", default="AI-Agent")
    parser_end = subparsers.add_parser("end")
    parser_end.add_argument("--task-id", required=True)
    parser_end.add_argument("--output", required=True)
    
    parser_record = subparsers.add_parser("record")
    parser_record.add_argument("--task-name", required=True)
    parser_record.add_argument("--prompt", required=True)
    parser_record.add_argument("--output", required=True)
    parser_record.add_argument("--project", default="")
    parser_record.add_argument("--agent", default="AI-Agent")
    parser_record.add_argument("--task-id", default="")  # 可选，用于传入 session_id
    parser_record.add_argument("--source", default="")  # 可选，标注来源平台（如 OpenCode）
    
    args = parser.parse_args()
    if args.command == "start":
        cmd_start(args)
    elif args.command == "end":
        cmd_end(args)
    elif args.command == "record":
        cmd_record(args)
