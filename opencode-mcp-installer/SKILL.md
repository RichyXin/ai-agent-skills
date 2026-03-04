---
name: opencode-mcp-installer
description: 自动安装和配置MCP工具。当用户提供GitHub地址时,自动克隆/下载MCP仓库,分析配置要求,更新OpenCode配置文件(/home/rentianxin/.config/opencode/opencode.jsonc),并设置MCP服务器。支持本地和远程MCP服务器。自动验证MCP服务器是否正常运行。
license: Complete terms in LICENSE.txt
---

# OpenCode MCP 安装器

自动安装和配置OpenCode的MCP工具，自动验证MCP服务器是否正常运行。

## 工作目录

- MCP文件缓存目录: `/home/rentianxin/.config/opencode/mega-tools`
- OpenCode配置文件: `/home/rentianxin/.config/opencode/opencode.jsonc`

## 安装流程

### 步骤1: 获取和分析MCP信息

用户提供的GitHub URL格式:
- 完整URL: `https://github.com/username/repo-name`
- 或者: `username/repo-name`

执行以下操作:
1. 提取仓库所有者和仓库名称
2. 调用GitHub API获取仓库README或配置文档
3. 查找`package.json`、`README.md`或其他配置文件,确定:
   - MCP类型(本地local/远程remote)
   - 启动命令(npx命令或脚本路径)
   - 是否需要环境变量
   - 依赖项(需npm install)

### 步骤2: 克隆/下载MCP项目

根据MCP类型处理:

**类型A: NPM包(可直接用npx运行)**
```bash
# 例如: npx -y @modelcontextprotocol/server-xyz
# 无需clone,直接使用npx
```

**类型B: 需要克隆的本地MCP**
```bash
cd /home/rentianxin/.config/opencode/mega-tools
git clone https://github.com/username/repo-name.git repo-name
cd repo-name
# 检查是否需要npm install
if [ -f "package.json" ]; then
  npm install
fi
```

### 步骤3: 生成MCP名称

从GitHub URL生成MCP名称:
```
https://github.com/SylphxAI/pdf-reader-mcp
→ mcp名称: "pdf-reader-mcp"
```

### 步骤4: 更新OpenCode配置

读取`/home/rentianxin/.config/opencode/opencode.jsonc`,在`mcp`对象中添加配置。

**本地MCP配置模板:**
```jsonc
{
  "type": "local",
  "command": ["npx", "-y", "package-name"],
  "enabled": true,
  "environment": {
    "ENV_VAR": "value"
  }
}
```

**克隆后的本地MCP配置模板:**
```jsonc
{
  "type": "local",
  "command": [
    "node",
    "/home/rentianxin/.config/opencode/mega-tools/repo-name/index.js"
  ],
  "enabled": true
}
```

**远程MCP配置模板:**
```jsonc
{
  "type": "remote",
  "url": "https://mcp-server-url.com/mcp",
  "enabled": true
}
```

### 步骤5: 验证配置

使用`opencode mcp list`检查MCP是否成功注册。

### 步骤6: 根据指导文档验证MCP服务器

根据MCP类型,用户需要根据指导文档配置MCP服务器:

**类型A: NPM包(可直接用npx运行)**
- 无需配置,直接使用npx启动

**类型B: 需要克隆的本地MCP**
- 确保MCP项目已克隆到缓存目录
- 查看项目README,根据指导配置环境变量和启动参数

## 示例安装

### 示例1: 安装pdf-reader-mcp

输入: `https://github.com/SylphxAI/pdf-reader-mcp`

流程:
1. 查看仓库README,发现使用npx启动
2. 生成配置:
```jsonc
"pdf-reader-mcp": {
  "type": "local",
  "command": ["npx", "-y", "@sylphxai/pdf-reader-mcp"],
  "enabled": true
}
```
3. 写入opencode.jsonc
4. 验证安装

### 示例2: 安装需要clone的MCP

输入: `https://github.com/example/custom-mcp`

流程:
1. 查看仓库,发现是TypeScript项目,需要npm install
2. 克隆到`/home/rentianxin/.config/opencode/mega-tools/custom-mcp`
3. 运行`npm install`
4. 查看package.json,找到启动脚本`node dist/index.js`
5. 生成配置:
```jsonc
"custom-mcp": {
  "type": "local",
  "command": [
    "node",
    "/home/rentianxin/.config/opencode/mega-tools/custom-mcp/dist/index.js"
  ],
  "enabled": true
}
```

## 特殊情况处理

### 带环境变量的MCP

如果MCP需要API Key或其他环境变量:
```jsonc
{
  "type": "local",
  "command": ["npx", "-y", "some-mcp"],
  "environment": {
    "API_KEY": "{env:MY_API_KEY}"
  },
  "enabled": true
}
```
提示用户设置环境变量。

### 脚本启动的MCP

如果MCP提供启动脚本:
```bash
# 例如: /path/to/repo/start.sh
command: ["/bin/bash", "/path/to/start.sh"]
```

## 检查清单

完成安装后,确保:
- [ ] MCP已添加到opencode.jsonc的mcp对象中
- [ ] 命令路径正确
- [ ] enabled设置为true
- [ ] 如果需要npm install已完成
- [ ] 运行`opencode mcp list`验证
