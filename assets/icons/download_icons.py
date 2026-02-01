#!/usr/bin/env python3
"""
IconPark 图标下载脚本
从 IconPark 官方源下载图标

使用方法:
    python download_icons.py

或下载特定图标:
    python download_icons.py --icon settings table export
"""

import os
import sys
import argparse
import urllib.request
import json
from pathlib import Path

# IconPark 图标源
ICONPARK_SOURCE = "https://iconpark.oceanengine.com/api/svg/getSvgId"
ICONPARK_DOWNLOAD = "https://iconpark.oceanengine.com/api/svg/download"

# 推荐图标列表
RECOMMENDED_ICONS = {
    # 主要功能图标
    'settings': '设置',
    'formula': '公式',
    'table': '表格',
    'refresh': '刷新',
    'export': '导出',
    'import': '导入',
    'preview': '预览',
    'edit': '编辑',

    # 文件操作
    'file': '文件',
    'folder': '文件夹',
    'folder-open': '打开文件夹',
    'file-addition': '新建文件',
    'save': '保存',

    # 数据操作
    'add': '添加',
    'minus': '减少',
    'delete': '删除',
    'copy': '复制',
    'search': '搜索',

    # 导航
    'home': '主页',
    'back': '返回',
    'next': '前进',
    'up': '向上',
    'down': '向下',

    # 帮助
    'help': '帮助',
    'info': '信息',
    'tips': '提示',

    # 其他
    'camera': '相机',
    'download': '下载',
    'upload': '上传',
    'close': '关闭',
    'check': '检查',
    'list': '列表',
    'menu': '菜单',
}


def download_icon(icon_name: str, output_dir: str = ".",
                  theme: str = "outline", size: int = 48,
                  stroke: int = 2, color: str = "#333333") -> bool:
    """
    下载单个图标

    Args:
        icon_name: 图标名称
        output_dir: 输出目录
        theme: 主题 (outline, filled, two-tone, multi-color)
        size: 图标尺寸
        stroke: 线条粗细
        color: 颜色

    Returns:
        是否成功
    """
    # IconPark 的直接下载链接格式
    url = f"https://iconpark.oceanengine.com/api/svg/getSvgId?id={icon_name}"

    try:
        # 首先获取 SVG ID
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

            if data.get('code') != 200:
                print(f"❌ 无法获取图标 '{icon_name}': {data.get('msg', 'Unknown error')}")
                return False

            svg_id = data.get('data', {}).get('id')
            if not svg_id:
                print(f"❌ 图标 '{icon_name}' 不存在")
                return False

        # 下载 SVG 文件
        download_url = f"https://iconpark.oceanengine.com/api/svg/download?id={svg_id}&theme={theme}&size={size}&stroke={stroke}&color={color.replace('#', '%23')}"

        req = urllib.request.Request(
            download_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        output_path = os.path.join(output_dir, f"{icon_name}.svg")

        with urllib.request.urlopen(req, timeout=10) as response:
            svg_content = response.read().decode('utf-8')

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)

        print(f"✅ 已下载: {icon_name}.svg")
        return True

    except Exception as e:
        print(f"❌ 下载 '{icon_name}' 失败: {e}")
        return False


def download_all_icons(output_dir: str = "."):
    """下载所有推荐图标"""
    os.makedirs(output_dir, exist_ok=True)

    print(f"开始下载 {len(RECOMMENDED_ICONS)} 个图标到 {output_dir}...")
    print("-" * 50)

    success_count = 0
    for icon_name in RECOMMENDED_ICONS:
        if download_icon(icon_name, output_dir):
            success_count += 1

    print("-" * 50)
    print(f"下载完成: {success_count}/{len(RECOMMENDED_ICONS)} 个图标")

    if success_count < len(RECOMMENDED_ICONS):
        print("\n提示: 部分图标下载失败，可能是网络问题或图标不存在")
        print("程序将使用 emoji 作为回退")


def main():
    parser = argparse.ArgumentParser(description='下载 IconPark 图标')
    parser.add_argument('--icons', '-i', nargs='+', help='指定要下载的图标名称')
    parser.add_argument('--output', '-o', default='.', help='输出目录 (默认: 当前目录)')
    parser.add_argument('--theme', '-t', default='outline',
                        choices=['outline', 'filled', 'two-tone', 'multi-color'],
                        help='图标主题 (默认: outline)')
    parser.add_argument('--size', '-s', type=int, default=48, help='图标尺寸 (默认: 48)')
    parser.add_argument('--stroke', type=int, default=2, help='线条粗细 (默认: 2)')
    parser.add_argument('--color', '-c', default='#333333', help='图标颜色 (默认: #333333)')

    args = parser.parse_args()

    if args.icons:
        # 下载指定图标
        os.makedirs(args.output, exist_ok=True)
        for icon_name in args.icons:
            download_icon(icon_name, args.output, args.theme, args.size, args.stroke, args.color)
    else:
        # 下载所有推荐图标
        download_all_icons(args.output)


if __name__ == '__main__':
    main()
