#!/usr/bin/env python3
import sys
import os
import re
import shutil
from datetime import datetime, timedelta


def parse_time_from_filename(filename):
    # Match logcat.log.xxx_YYYY_MM_DD_HH_MM_SS.gz
    match = re.search(r"(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})", filename)
    if match:
        try:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6)),
            )
        except ValueError:
            return None
    return None


def extract_logs(source_dir, jira_key, target_time_str):
    try:
        # Support formats like "2026-02-27 15:05:01" or "2026_02_27_15_05_01"
        clean_time_str = re.sub(r"[^\d]", "", target_time_str)
        if len(clean_time_str) != 14:
            print(
                f"Error: 无法解析目标时间格式 '{target_time_str}'，请提供如 '2026-02-27 15:05:01' 格式的时间"
            )
            return

        target_time = datetime.strptime(clean_time_str, "%Y%m%d%H%M%S")
    except Exception as e:
        print(f"Error: 解析时间失败 - {e}")
        return

    output_dir = os.path.expanduser(f"~/Downloads/{jira_key}")
    os.makedirs(output_dir, exist_ok=True)

    # 1. 收集所有 .gz 文件及其结束时间
    all_log_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".gz"):
                file_time = parse_time_from_filename(file)
                if file_time:
                    all_log_files.append({
                        "path": os.path.join(root, file),
                        "name": file,
                        "end_time": file_time,
                        "is_gz": True
                    })
            elif file == "logcat.log":
                all_log_files.append({
                    "path": os.path.join(root, file),
                    "name": file,
                    "end_time": datetime.max, # Treat as the latest log
                    "is_gz": False
                })

    if not all_log_files:
        print(json.dumps({"status": "error", "message": "未在源码目录找到任何有效的日志文件(.gz 或 logcat.log)"}, ensure_ascii=False))
        return

    # 2. 按结束时间排序
    all_log_files.sort(key=lambda x: x["end_time"])

    # 3. 定义目标范围：前后各 4 分钟
    range_start = target_time - timedelta(minutes=4)
    range_end = target_time + timedelta(minutes=4)

    # 4. 筛选有重叠时间段的文件
    found_files = []
    for i, log_file in enumerate(all_log_files):
        # 估计开始时间是上一个文件的结束时间（第一个文件假设从很久以前开始）
        start_time = all_log_files[i-1]["end_time"] if i > 0 else datetime.min
        end_time = log_file["end_time"]
        
        # 判断 [start_time, end_time] 是否与 [range_start, range_end] 有交集
        if max(start_time, range_start) <= min(end_time, range_end):
            src_path = log_file["path"]
            dest_path = os.path.join(output_dir, log_file["name"])
            
            if not os.path.exists(dest_path):
                shutil.copy2(src_path, dest_path)
            found_files.append({
                "src": src_path,
                "dest": dest_path,
                "time": end_time,
                "is_gz": log_file["is_gz"]
            })
    if found_files:
        found_files.sort(key=lambda x: x["time"]) # Sort by time
        merged_filename = f"merged_{jira_key}_{clean_time_str}.log"
        merged_filepath = os.path.join(output_dir, merged_filename)
        
        # 定义精确的时间范围字符串用于比对 (MM-DD HH:MM:SS)
        # 假设日志中的年份与目标时间一致
        log_range_start = range_start.strftime("%m-%d %H:%M:%S")
        log_range_end = range_end.strftime("%m-%d %H:%M:%S")
        
        # 日志时间正则表达式: 02-28 17:36:01.123
        time_pattern = re.compile(r'^(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d{3})')
        
        import gzip
        with open(merged_filepath, 'w') as outfile:
            last_line_included = False
            for file_info in found_files:
                src = file_info["src"]
                # 打开文件（处理压缩或普通文本）
                f = gzip.open(src, 'rt', errors='ignore') if file_info["is_gz"] else open(src, 'r', errors='ignore')
                
                with f as infile:
                    for line in infile:
                        match = time_pattern.match(line)
                        if match:
                            # 提取时间部分用于比较: MM-DD HH:MM:SS
                            line_time_str = f"{match.group(1)} {match.group(2).split('.')[0]}"
                            if log_range_start <= line_time_str <= log_range_end:
                                outfile.write(line)
                                last_line_included = True
                            else:
                                last_line_included = False
                        else:
                            # 如果这一行没有时间戳（可能是多行log的后续内容），随上一行决定是否保留
                            if last_line_included:
                                outfile.write(line)
        found_filenames = [os.path.basename(f["src"]) for f in found_files]

    if found_files:
        print(
            json.dumps(
                {
                    "status": "success",
                    "message": f"成功提取了 {len(found_files)} 个日志文件并合并到 {merged_filepath}",
                    "output_dir": output_dir,
                    "merged_file": merged_filename,
                    "source_files": found_filenames,
                },
                ensure_ascii=False,
                indent=2
            )
        )
    else:
        print(
            json.dumps(
                {
                    "status": "warning",
                    "message": "未找到指定时间范围内的日志文件，请确认输入路径或时间是否准确",
                    "output_dir": output_dir,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    import json

    if len(sys.argv) < 4:
        print(
            json.dumps(
                {
                    "error": "用法: python3 extract_logs.py <日志解压目录> <Jira单号> <目标时间(如'2026-02-27 15:05:01')>"
                }
            )
        )
        sys.exit(1)

    source_dir = sys.argv[1]
    jira_key = sys.argv[2]
    target_time_str = sys.argv[3]

    if not os.path.exists(source_dir):
        print(json.dumps({"error": f"来源目录不存在: {source_dir}"}))
        sys.exit(1)

    extract_logs(source_dir, jira_key, target_time_str)
