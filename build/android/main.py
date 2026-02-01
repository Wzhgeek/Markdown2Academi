#!/usr/bin/env python3
"""
Markdown2Academia - Android 入口
"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from gui.mobile.main_app import main

if __name__ == '__main__':
    main()
