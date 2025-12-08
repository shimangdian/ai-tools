# OCR 服务 - 使用 Tesseract.js

本项目使用 Node.js + Tesseract.js 实现 OCR 功能，无需安装系统级 Tesseract 引擎。

## 安装

### 1. 安装 Node.js

确保系统已安装 Node.js（建议 v14 或更高版本）：

```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt-get install nodejs npm

# 或访问 https://nodejs.org/ 下载安装
```

### 2. 安装依赖

```bash
cd daily-news

# 安装 Node.js 依赖（Tesseract.js）
npm install

# 安装 Python 依赖
pip install -r requirements.txt
```

## 使用

OCR 服务会自动在运行时调用：

```bash
# 立即运行一次（测试）
python -m app.main --run-once

# 启动定时任务
python -m app.main
```

## 工作原理

1. Python 服务调用 Node.js 脚本 ([ocr_service.js](ocr_service.js))
2. Node.js 使用 Tesseract.js 下载并处理图片
3. 第一次运行时会自动下载中英文语言包（约 10-20 秒）
4. OCR 结果以 JSON 格式返回给 Python

## 测试 OCR 服务

```bash
# 使用 Node.js 直接测试
node ocr_service.js <图片URL或本地路径>

# 示例
node ocr_service.js https://example.com/image.jpg
```

## 功能特点

- ✅ 无需安装系统级 Tesseract 引擎
- ✅ 自动下载语言包（首次运行）
- ✅ 支持中英文识别
- ✅ 支持 URL 和本地文件
- ✅ 跨平台（Windows/macOS/Linux）

## 文件说明

- [ocr_service.js](ocr_service.js) - Node.js OCR 服务脚本
- [package.json](package.json) - Node.js 依赖配置
- [app/ocr_service.py](app/ocr_service.py) - Python OCR 服务封装
