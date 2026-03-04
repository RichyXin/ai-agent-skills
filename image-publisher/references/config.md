# 配置参考

## 配置方式：使用 .env 文件

在技能目录创建 `.env` 文件：

```bash
cd ~/.claude/skills/image-publisher
cp .env.example .env
```

## 通用配置

| 变量名 | 必需 | 说明 | 可选值 |
|--------|------|------|--------|
| `PROVIDER_TYPE` | 是 | 图床类型 | `github` / `s3` |

---

## GitHub 图床配置

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `GITHUB_TOKEN` | 是 | GitHub Personal Access Token | `ghp_xxxxxxxx` |
| `GITHUB_USER` | 是 | GitHub 用户名 | `maoruibin` |
| `GITHUB_REPO` | 是 | 仓库名 | `image-host` |
| `GITHUB_BRANCH` | 否 | 分支名 | `master`（默认） |
| `GITHUB_IMAGES_DIR` | 否 | 图片目录 | `images`（默认） |
| `GITHUB_PATH_MODE` | 否 | 路径模式 | `flat`（平铺）或 `date`（按年/月/日） |

### 返回的链接格式

#### 原始链接

```
https://raw.githubusercontent.com/{user}/{repo}/{branch}/{dir}/{filename}
```

#### CDN 链接（jsDelivr，推荐）

```
https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{dir}/{filename}
```

### 路径模式说明

#### flat 模式（默认）

图片平铺存储在单一目录：

```
images/screenshot.png
images/photo.jpg
```

#### date 模式

按年/月/日分层存储：

```
images/2026/01/12/screenshot.png
images/2026/01/13/photo.jpg
```

适合图片较多时使用，便于管理和归档。

---

## S3 图床配置

支持所有 S3 兼容的云存储：七牛云、阿里云 OSS、腾讯云 COS、MinIO 等。

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `S3_ACCESS_KEY_ID` | 是 | S3 Access Key ID | `your_access_key` |
| `S3_SECRET_ACCESS_KEY` | 是 | S3 Secret Access Key | `your_secret_key` |
| `S3_BUCKET` | 是 | Bucket 名称 | `my-bucket` |
| `S3_ENDPOINT` | 是 | S3 Endpoint | `s3.cn-south-1.qiniucs.com` |
| `S3_REGION` | 否 | S3 区域 | `cn-south-1` |
| `S3_IMAGES_DIR` | 否 | 图片目录前缀 | `images`（默认） |
| `S3_PATH_MODE` | 否 | 路径模式 | `flat`（平铺）或 `date`（按年/月/日） |
| `S3_DOMAIN` | 否 | 自定义域名（CDN） | `https://cdn.example.com` |

### 七牛云 S3 配置

七牛云对象存储完全兼容 S3 协议。

| 配置项 | 七牛云示例 |
|--------|-----------|
| `S3_ENDPOINT` | `s3.cn-south-1.qiniucs.com` |
| `S3_REGION` | `cn-south-1` |

**七牛云各区域 Endpoint：**

| 区域 | Endpoint |
|------|----------|
| 华东 | `s3.cn-east-1.qiniucs.com` |
| 华北 | `s3.cn-north-1.qiniucs.com` |
| 华南 | `s3.cn-south-1.qiniucs.com` |
| 北美 | `s3.us-north-1.qiniucs.com` |

### 阿里云 OSS S3 配置

阿里云 OSS 支持 S3 协议，需要在 OSS 控制台开启。

| 配置项 | 阿里云 OSS 示例 |
|--------|----------------|
| `S3_ENDPOINT` | `oss-cn-hangzhou.aliyuncs.com` |
| `S3_REGION` | `cn-hangzhou` |

### 腾讯云 COS S3 配置

| 配置项 | 腾讯云 COS 示例 |
|--------|----------------|
| `S3_ENDPOINT` | `cos.ap-guangzhou.myqcloud.com` |
| `S3_REGION` | `ap-guangzhou` |

### S3 URL 格式

#### 默认 URL

```
https://{bucket}.{endpoint}/{key}
```

例如：`https://maoimage.s3.cn-south-1.qiniucs.com/images/screenshot.png`

#### 自定义域名 URL

如果配置了 `S3_DOMAIN`，则返回：

```
https://cdn.example.com/images/screenshot.png
```

---

## 获取 GitHub Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选权限：
   - ✅ repo (Full control of private repositories)
4. 点击 "Generate token"
5. 复制 token（只显示一次！）

## 支持的图片格式

| 格式 | 扩展名 |
|------|--------|
| PNG | `.png` |
| JPEG | `.jpg`, `.jpeg` |
| GIF | `.gif` |
| WebP | `.webp` |
| SVG | `.svg` |
| BMP | `.bmp` |
| ICO | `.ico` |

## 依赖安装

```bash
# GitHub 图床
pip install requests

# S3 图床
pip install boto3

# 两者都装
pip install requests boto3
```
