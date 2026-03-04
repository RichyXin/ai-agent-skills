---
name: git-commit-message
description: 根据Megatronix团队规范生成符合格式的git提交消息
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: git
---

# Git Commit Message 规范化技能

## 专业背景
我是用于规范化git提交消息格式的AI技能，基于Megatronix团队的提交约定开发。专门用于生成和验证符合团队标准的git提交消息格式，确保所有提交遵循统一的规范。

## 核心能力

### 代码变更分析
- 自动分析git status和diff
- 识别修改的文件类型和范围
- 智能判断变更类型（新增、修改、删除、bug修复）
- 支持多文件变更的综合分析
- 如果传入的参数中，有jira连接，可以调用mcp jira 查看问题描述等信息，根据问题描述自动填充问题原因和修改方案

### 智能消息生成
- 基于代码变更内容生成合适的提交类型
- 自动生成简洁准确的描述
- 分析变更影响确定合适的类型（Task/Bugfix）

### 交互式编辑
- 弹出交互对话框进行消息编辑
- 提供字段填写提示（Jira-Id等）
- 支持用户确认、修改和补充信息
- 实时验证格式正确性

### 格式验证与规范化
- 验证消息格式符合团队规范
- 自动填充签名信息
- 确保消息长度和结构正确
- 提供格式错误提示和修正建议

## 格式规范

### 消息结构
提交消息必须遵循以下结构：

```
第一行：类型[可选项目名]: 简短描述
空行
问题原因:仅bugfix类型需要
修改方案：仅bugfix类型需要

Jira-Id: 编号（可多个，用&连接）
空行
空行
Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

### 示例
```
Task[Monterey]: 语音和Toast的默认窗口层级调整

Jira-Id: CF-57223


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

```
Bugfix: 修改弹窗的可见文言从返回变成"关闭"

问题原因: XX
修改方案: XX

Jira-Id: CF-55236


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

```
Task[Pebblebeach]: Pebblebeach的代码初始化

Jira-Id: PB-35


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

## 验证规则

### 必需字段
- 类型（Task、Bugfix之一）
- 描述（简洁说明变更内容）
- Jira-Id（至少一个Jira编号）
- Signed-off-by签名

### 可选字段
- 问题原因：仅bugfix类型需要，根据上下文自动填充
- 修改方案：仅bugfix类型需要，根据上下文自动填充

### 格式检查
- 第一行必须以类型开头
- 包含冒号分隔符
- 项目名可选，用方括号包围
- 第一行长度不超过120字符
- 描述采用简体中文
- 签名固定为 tianxin.ren <tianxin.ren@megatronix.co>

## 模板

### 默认模板
```
类型[项目]: 描述

问题原因: XX
修改方案: XX

Jira-Id: ID


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

### 带项目范围模板
```
类型[项目名]: 描述变更内容

问题原因: XX
修改方案: XX

Jira-Id: JIRA-编号


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

### 多Jira模板
```
类型: 描述

问题原因: XX
修改方案: XX

Jira-Id: ID1 & ID2


Signed-off-by: tianxin.ren <tianxin.ren@megatronix.co>
```

## 使用流程

### 1. 分析变更
```
git status  # 查看当前修改状态
git diff    # 查看具体变更内容
```

### 2. 生成消息
技能会自动：
- 分析修改的文件和内容
- 判断变更类型（Task/Bugfix）
- 生成初步描述

### 3. 交互编辑
弹出对话框让用户：
- 确认/修改生成的类型和描述
- 填写Jira-Id（支持多个，用&连接）
- 添加额外说明（可选）
- 确认最终消息

### 4. 提交确认
- 显示完整的commit message
- 用户确认后执行git commit

## 命令示例

### 基本使用
```bash
# 分析当前变更并生成commit message
git-commit-smart

# 指定特定文件
git-commit-smart --files "src/main.java,src/utils.java"

# 预览模式（不实际提交）
git-commit-smart --preview
```

### 交互流程示例
```
变更分析中...
发现修改：3个文件（2个新增，1个修改）
建议类型：Task

[交互对话框]
类型: Task [Monterey]
描述: 添加用户认证功能
Jira-Id: AUTH-123 & AUTH-124
额外说明: [可选]

确认提交？ (y/n)
```

## 智能分析规则

### 类型判断逻辑
- **Task**: 新功能、特性添加、配置变更
- **Bugfix**: 修复bug、错误处理、性能优化

### 文件类型分析
- `.java/.kt`: Android/Java代码变更
- `.xml`: 布局/配置变更
- `.md`: 文档更新
- 图片/资源: 资源更新

### 描述生成
- 基于文件名和修改内容生成
- 提取关键变更点
- 保持简洁明了

## 使用说明

1. 确保在git仓库根目录执行
2. 有未提交的变更时使用
3. 支持暂存区(staged)和工作区(unstaged)变更
4. 自动处理签名，避免手动输入

## 元数据
- 适用范围：Megatronix团队git提交规范