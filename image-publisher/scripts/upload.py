#!/usr/bin/env python3
"""
Image Publisher - Upload local images to image hosting services and get accessible URLs.
Supports GitHub and S3-compatible storage (Qiniu, Aliyun OSS, Tencent COS, etc.).
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


# Default values
DEFAULT_BRANCH = "master"
DEFAULT_IMAGES_DIR = "images"
DEFAULT_PATH_MODE = "flat"

# Supported image formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}


def load_env():
    """Load configuration from .env file in the skill directory."""
    skill_dir = Path(__file__).parent.parent
    env_file = skill_dir / ".env"

    if not env_file.exists():
        print(f"Error: .env file not found at {env_file}")
        print("Please copy .env.example to .env and configure your settings.")
        sys.exit(1)

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    return config


def get_image_path(path_mode, images_dir, filename):
    """Build the target path for an image based on path mode."""
    images_dir = images_dir.strip("/")

    if path_mode == "date":
        # Use YYYY/MM/DD format
        date_path = datetime.now().strftime("%Y/%m/%d")
        return f"{images_dir}/{date_path}/{filename}"
    else:
        # Flat mode
        return f"{images_dir}/{filename}"


# =============================================================================
# GitHub Provider
# =============================================================================

def upload_to_github(config, image_path):
    """Upload image to GitHub repository."""
    # Validate GitHub config
    required = ["GITHUB_TOKEN", "GITHUB_USER", "GITHUB_REPO"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"Error: Missing required GitHub configuration: {', '.join(missing)}")
        sys.exit(1)

    # Read image content
    with open(image_path, "rb") as f:
        content = f.read()

    import base64
    content_b64 = base64.b64encode(content).decode()

    filename = Path(image_path).name
    branch = config.get("GITHUB_BRANCH", DEFAULT_BRANCH)
    images_dir = config.get("GITHUB_IMAGES_DIR", DEFAULT_IMAGES_DIR)
    path_mode = config.get("GITHUB_PATH_MODE", DEFAULT_PATH_MODE)

    target_path = get_image_path(path_mode, images_dir, filename)

    # Check if file already exists
    url = f"https://api.github.com/repos/{config['GITHUB_USER']}/{config['GITHUB_REPO']}/contents/{target_path}"
    headers = {
        "Authorization": f"Bearer {config['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers, params={"ref": branch})
    if response.status_code == 200:
        print(f"Warning: File already exists at {target_path}")
        resp = input("Overwrite? (y/N): ").strip().lower()
        if resp != "y":
            print("Upload cancelled.")
            sys.exit(0)
        # Need SHA for update
        sha = response.json().get("sha")
    else:
        sha = None

    # Prepare API request
    data = {
        "message": f"Upload image: {filename}",
        "content": content_b64,
        "branch": branch
    }
    if sha:
        data["sha"] = sha

    # Upload
    print(f"Uploading {filename} to GitHub: {target_path}...")
    response = requests.put(url, headers=headers, json=data)

    if response.status_code not in (200, 201):
        print(f"Error: Upload failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)

    # Build URLs
    raw_url = f"https://raw.githubusercontent.com/{config['GITHUB_USER']}/{config['GITHUB_REPO']}/{branch}/{target_path}"
    cdn_url = f"https://cdn.jsdelivr.net/gh/{config['GITHUB_USER']}/{config['GITHUB_REPO']}@{branch}/{target_path}"

    print("Upload successful!")

    return {
        "provider": "github",
        "filename": filename,
        "path": target_path,
        "raw_url": raw_url,
        "cdn_url": cdn_url,
        "url": cdn_url  # Default URL
    }


# =============================================================================
# S3 Provider (Qiniu, Aliyun OSS, Tencent COS, etc.)
# =============================================================================

def upload_to_s3(config, image_path):
    """Upload image to S3-compatible storage."""
    if not HAS_BOTO3:
        print("Error: boto3 module not found. Install with: pip install boto3")
        sys.exit(1)

    # Validate S3 config
    required = ["S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY", "S3_BUCKET", "S3_ENDPOINT"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"Error: Missing required S3 configuration: {', '.join(missing)}")
        sys.exit(1)

    # Debug: print config (without secret)
    print(f"Debug: S3_ENDPOINT={config['S3_ENDPOINT']}")
    print(f"Debug: S3_BUCKET={config['S3_BUCKET']}")
    print(f"Debug: S3_ACCESS_KEY_ID={config['S3_ACCESS_KEY_ID'][:10]}...")
    print(f"Debug: S3_SECRET_ACCESS_KEY={config['S3_SECRET_ACCESS_KEY'][:10]}...")

    filename = Path(image_path).name
    images_dir = config.get("S3_IMAGES_DIR", DEFAULT_IMAGES_DIR)
    path_mode = config.get("S3_PATH_MODE", DEFAULT_PATH_MODE)
    custom_domain = config.get("S3_DOMAIN", "")

    # Build S3 key
    s3_key = get_image_path(path_mode, images_dir, filename)

    # Create S3 client
    from botocore.config import Config

    region = config.get("S3_REGION")

    # Create S3 client
    # Try with boto3 session
    from botocore.config import Config
    from botocore import UNSIGNED

    endpoint = config['S3_ENDPOINT']
    if not endpoint.startswith('https://') and not endpoint.startswith('http://'):
        endpoint = f"https://{endpoint}"

    # Use us-east-1 as signature region if not specified
    sig_region = region if region else "us-east-1"

    session = boto3.Session(
        aws_access_key_id=config["S3_ACCESS_KEY_ID"],
        aws_secret_access_key=config["S3_SECRET_ACCESS_KEY"],
        region_name=sig_region
    )

    s3 = session.client(
        "s3",
        endpoint_url=endpoint,
        use_ssl=True
    )
    bucket = config["S3_BUCKET"]

    # Check if file already exists
    file_exists = False
    try:
        s3.head_object(Bucket=bucket, Key=s3_key)
        file_exists = True
    except ClientError as e:
        # 404 means file doesn't exist, which is good
        if e.response["Error"]["Code"] == "404":
            pass
        # 403 might mean file exists but no permission to check, just skip check
        elif e.response["Error"]["Code"] == "403":
            pass
        else:
            # Other errors, warn but continue
            print(f"Warning: Could not check if file exists: {e}")

    if file_exists:
        print(f"Warning: File already exists at {s3_key}")
        resp = input("Overwrite? (y/N): ").strip().lower()
        if resp != "y":
            print("Upload cancelled.")
            sys.exit(0)

    # Upload
    print(f"Uploading {filename} to S3: {s3_key}...")
    try:
        s3.upload_file(
            str(image_path),
            bucket,
            s3_key,
            ExtraArgs={"ContentType": get_content_type(image_path)}
        )
    except Exception as e:
        print(f"Error: Upload failed: {e}")
        sys.exit(1)

    print("Upload successful!")

    # Build URLs
    # Default S3 URL format
    raw_url = f"https://{bucket}.{config['S3_ENDPOINT']}/{s3_key}"

    # Use custom domain if provided
    if custom_domain:
        custom_domain = custom_domain.rstrip("/")
        url = f"{custom_domain}/{s3_key}"
    else:
        url = raw_url

    return {
        "provider": "s3",
        "filename": filename,
        "path": s3_key,
        "raw_url": raw_url,
        "url": url
    }


def get_content_type(image_path):
    """Get Content-Type for image file."""
    ext = Path(image_path).suffix.lower()
    content_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp",
        ".ico": "image/x-icon"
    }
    return content_types.get(ext, "image/png")


# =============================================================================
# Main
# =============================================================================

def upload_image(image_path):
    """Upload an image to the configured provider."""
    # Load configuration
    config = load_env()

    # Validate image file
    image_path = Path(image_path).expanduser()
    if not image_path.exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"Error: Unsupported file format: {image_path.suffix}")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        sys.exit(1)

    # Get provider type
    provider = config.get("PROVIDER_TYPE", "github").lower()

    if provider == "s3":
        result = upload_to_s3(config, image_path)
    elif provider == "github":
        result = upload_to_github(config, image_path)
    else:
        print(f"Error: Unsupported provider type: {provider}")
        print("Supported providers: github, s3")
        sys.exit(1)

    # Print result
    print()
    print(f"Filename:  {result['filename']}")
    print(f"Path:      {result['path']}")
    print(f"URL:       {result['url']}")
    if "cdn_url" in result:
        print(f"CDN URL:  {result['cdn_url']}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload.py <image_path>")
        print("Example: python upload.py ~/Desktop/screenshot.png")
        sys.exit(1)

    upload_image(sys.argv[1])
