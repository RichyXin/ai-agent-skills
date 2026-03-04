---
name: hprof-analyzer
description: |
  分析 Java/Android hprof 堆转储文件，检测内存泄漏，生成结构化分析报告。
  适用于分析 Java 堆内存、识别内存泄漏、分析对象引用链。
  当用户提供 hprof 文件路径或请求分析内存问题时自动激活。
---

# Hprof 内存分析 Skill

## 功能概述

本 Skill 用于分析 Java/Android 的 hprof 堆转储文件，帮助识别内存泄漏、分析内存分布、生成诊断报告。

## 适用场景

- 分析 Android 应用内存泄漏
- 诊断 Java 服务内存问题
- 分析堆内存对象分布
- 识别大对象和内存热点

## 工作流程

```
1. 验证 hprof 文件格式
   ├── 检查文件头 (JAVA PROFILE 1.0.x)
   ├── 验证版本兼容性
   └── 确认文件完整性

2. 提取堆内存统计
   ├── 解析堆记录
   ├── 统计对象数量和类型
   └── 计算内存分布

3. 分析内存模式
   ├── 识别大对象
   ├── 检测重复对象模式
   └── 分析类加载情况

4. 生成诊断报告
   ├── 内存概览摘要
   ├── 疑似泄漏点
   └── 优化建议
```

## 使用方法

### 基本用法

```bash
# 解析 hprof 文件
python3 ~/.agents/skills/hprof-analyzer/scripts/hprof_analyzer.py /path/to/dump.hprof

# 生成完整分析报告
python3 ~/.agents/skills/hprof-analyzer/scripts/hprof_analyzer.py /path/to/dump.hprof --output report.md
```

### 在对话中使用

当用户提供 hprof 文件时，自动激活本 skill：

**示例对话：**

User: "帮我分析这个 hprof 文件：/path/to/heap_dump.hprof"

Assistant: "我将为您分析这个 hprof 文件。让我先检查文件格式和基本信息..."

[执行分析流程]

"分析完成！以下是详细的内存分析报告..."

