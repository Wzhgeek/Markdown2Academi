#!/usr/bin/env python3
"""
Markdown to Academia - 桌面端入口
学术论文格式转换工具
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.desktop.main_window import MainWindow


def main():
    """主入口函数"""
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
