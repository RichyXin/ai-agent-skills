#!/usr/bin/env python3
import sys
import re
import json


def parse_jira(input_str):
    # Regex to match Jira key like CF-12345
    match = re.search(r"(CF|MRY|PB)-\d+", input_str, re.IGNORECASE)

    if not match:
        return {
            "error": "未能在输入中找到有效的 Ford 项目 Jira 单号(CF-xxx, MRY-xxx, PB-xxx)"
        }

    jira_key = match.group(0).upper()
    prefix = match.group(1).upper()

    project_info = {
        "jira_key": jira_key,
        "jira_url": f"http://jira.i-tetris.com/browse/{jira_key}",
    }

    if prefix == "CF":
        project_info["model"] = "Cardiff"
        project_info["platform"] = "8255"
    elif prefix == "MRY":
        project_info["model"] = "Monterey"
        project_info["platform"] = "8155"
    elif prefix == "PB":
        project_info["model"] = "PebbleBeach"
        project_info["platform"] = "8155"

    return project_info


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供 Jira 链接或单号"}))
        sys.exit(1)

    input_str = sys.argv[1]
    result = parse_jira(input_str)
    print(json.dumps(result, ensure_ascii=False, indent=2))
