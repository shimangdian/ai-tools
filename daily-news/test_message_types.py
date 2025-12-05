#!/usr/bin/env python3
"""
测试企业微信不同消息类型的脚本
"""
import requests
import sys

MESSAGE_SENDER_URL = "http://localhost:8000"
IMAGE_URL = "https://mmbiz.qpic.cn/mmbiz_jpg/stO6C6MJmPDfdzicXkCF5q7yD13bhsPkEKiaPXxE6QMnoh7SCZEEGOvdRR8yNMWQdGxeT8oKaTsV92IktSoD9rbg/640"


def test_text():
    """测试 text 类型（纯文本）"""
    print("测试 text 类型...")
    data = {
        "title": "文本消息测试",
        "content": "这是一条纯文本消息",
        "message_type": "text",
        "sender_type": "wecom"
    }
    response = requests.post(f"{MESSAGE_SENDER_URL}/send", json=data)
    print(f"结果: {response.json()}\n")


def test_markdown():
    """测试 markdown 类型（不显示图片）"""
    print("测试 markdown 类型（不支持图片）...")
    data = {
        "title": "Markdown 消息测试",
        "content": f"## 标题\n\n**加粗文本**\n\n![图片]({IMAGE_URL})\n\n*注意：图片只会显示为文字*",
        "message_type": "markdown",
        "sender_type": "wecom"
    }
    response = requests.post(f"{MESSAGE_SENDER_URL}/send", json=data)
    print(f"结果: {response.json()}\n")


def test_markdown_v2():
    """测试 markdown_v2 类型（支持图片）"""
    print("测试 markdown_v2 类型（支持图片，推荐）...")
    content = f"""# 📰 每日早报测试

**日期**: 2025-12-05

这是 markdown_v2 类型，支持更丰富的格式：

## 支持的功能
- *斜体*
- **加粗**
- 列表
- 表格
- 图片

![早报图片]({IMAGE_URL})

---
*markdown_v2 完整支持图片显示*"""

    data = {
        "title": "Markdown V2 测试",
        "content": content,
        "message_type": "markdown_v2",
        "sender_type": "wecom"
    }
    response = requests.post(f"{MESSAGE_SENDER_URL}/send", json=data)
    print(f"结果: {response.json()}\n")


def test_news():
    """测试 news 类型（显示图片卡片）"""
    print("测试 news 类型（图文卡片）...")
    data = {
        "title": "📰 每日早报 - 图文消息",
        "content": IMAGE_URL,
        "message_type": "news",
        "sender_type": "wecom",
        "extra": {
            "picurl": IMAGE_URL,
            "url": IMAGE_URL,
            "description": "这是一条带图片的图文消息"
        }
    }
    response = requests.post(f"{MESSAGE_SENDER_URL}/send", json=data)
    print(f"结果: {response.json()}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "text":
            test_text()
        elif test_type == "markdown":
            test_markdown()
        elif test_type == "markdown_v2":
            test_markdown_v2()
        elif test_type == "news":
            test_news()
        else:
            print(f"未知类型: {test_type}")
            print("用法: python test_message_types.py [text|markdown|markdown_v2|news]")
    else:
        print("测试所有消息类型...\n")
        test_text()
        test_markdown()
        test_markdown_v2()
        test_news()
        print("测试完成！请查看企业微信群消息")
