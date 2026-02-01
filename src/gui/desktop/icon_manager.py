"""
图标管理器 - 处理 IconPark 图标加载和缓存
支持 SVG 和 PNG 格式
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
import os
import sys
from typing import Dict, Tuple, Optional, Union

# 尝试导入 CairoSVG，如果不存在或系统库缺失则使用 PNG 回退
try:
    import cairosvg
    # 测试是否能正常初始化
    cairosvg.svg2png(bytestring=b'<svg/>')
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    print(f"[IconManager] CairoSVG 不可用: {e}")
    print("[IconManager] 将使用 PNG 图标或 emoji 回退")
    CAIROSVG_AVAILABLE = False


class IconManager:
    """管理 IconPark 图标"""

    # 标准图标尺寸
    SIZES = {
        'small': (16, 16),
        'medium': (24, 24),
        'large': (32, 32),
        'xlarge': (48, 48)
    }

    # 默认图标颜色（深色主题）
    DEFAULT_COLOR = "#333333"

    def __init__(self, icons_dir: str = "assets/icons"):
        self.icons_dir = self._resource_path(icons_dir)
        self._cache: Dict[str, ImageTk.PhotoImage] = {}
        self._fallback_to_emoji = True  # 如果图标加载失败，使用 emoji

    def _resource_path(self, relative_path: str) -> str:
        """获取资源绝对路径（支持 PyInstaller）"""
        try:
            # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def get_icon(self, icon_name: str,
                 size: Union[str, Tuple[int, int]] = "medium",
                 color: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
        """
        获取图标

        Args:
            icon_name: 图标名称（如 'settings', 'table'）
            size: 尺寸 ('small', 'medium', 'large', 'xlarge') 或 (宽, 高)
            color: 可选的十六进制颜色 (#RRGGBB)

        Returns:
            ImageTk.PhotoImage 或 None
        """
        # 确定尺寸
        if isinstance(size, str):
            size_tuple = self.SIZES.get(size, self.SIZES['medium'])
        else:
            size_tuple = size

        # 缓存键
        cache_key = f"{icon_name}_{size_tuple}_{color}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # 尝试加载 SVG
        icon = None
        if CAIROSVG_AVAILABLE:
            icon = self._load_svg(icon_name, size_tuple, color)

        # SVG 失败则尝试 PNG
        if icon is None:
            icon = self._load_png(icon_name, size_tuple)

        if icon:
            self._cache[cache_key] = icon

        return icon

    def _load_svg(self, icon_name: str, size: Tuple[int, int],
                  color: Optional[str]) -> Optional[ImageTk.PhotoImage]:
        """加载 SVG 图标"""
        svg_path = os.path.join(self.icons_dir, f"{icon_name}.svg")

        if not os.path.exists(svg_path):
            return None

        try:
            # 读取 SVG 内容
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # 如果指定了颜色，替换 SVG 中的颜色
            if color:
                svg_content = self._apply_color_to_svg(svg_content, color)

            # 转换为 PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size[0],
                output_height=size[1]
            )

            # 加载为 PIL Image
            image = Image.open(io.BytesIO(png_data))
            return ImageTk.PhotoImage(image)

        except Exception as e:
            print(f"Error loading SVG {icon_name}: {e}")
            return None

    def _load_png(self, icon_name: str, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
        """加载 PNG 图标"""
        png_path = os.path.join(self.icons_dir, f"{icon_name}.png")

        if not os.path.exists(png_path):
            return None

        try:
            image = Image.open(png_path)
            # 使用高质量缩放
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading PNG {icon_name}: {e}")
            return None

    def _apply_color_to_svg(self, svg_content: str, color: str) -> str:
        """将颜色应用到 SVG"""
        # 移除 # 前缀
        color = color.lstrip('#')

        # 替换 stroke 和 fill 颜色
        import re

        # 替换 stroke="..." 和 fill="..."
        svg_content = re.sub(
            r'stroke="[^"]*"',
            f'stroke="#{color}"',
            svg_content
        )
        svg_content = re.sub(
            r'fill="[^"]*"',
            f'fill="#{color}"',
            svg_content
        )

        # 替换 stroke='...' 和 fill='...'
        svg_content = re.sub(
            r"stroke='[^']*'",
            f"stroke='#{color}'",
            svg_content
        )
        svg_content = re.sub(
            r"fill='[^']*'",
            f"fill='#{color}'",
            svg_content
        )

        return svg_content

    def create_button(self, parent, icon_name: str, text: str = "",
                     command=None, size: Union[str, Tuple[int, int]] = "medium",
                     compound: str = "left", **kwargs) -> ttk.Button:
        """
        创建带图标的按钮

        Args:
            parent: 父组件
            icon_name: 图标名称
            text: 按钮文本
            command: 点击回调
            size: 图标尺寸
            compound: 图标位置 ('left', 'right', 'top', 'bottom', 'none')
            **kwargs: 其他 ttk.Button 参数
        """
        icon = self.get_icon(icon_name, size)

        if icon is None and not text:
            # 既没有图标也没有文本，使用 emoji 回退
            text = self._get_emoji_fallback(icon_name)

        btn = ttk.Button(
            parent,
            text=text,
            image=icon if icon else None,
            compound=compound if icon and text else "none",
            command=command,
            **kwargs
        )

        # 保持引用防止垃圾回收
        if icon:
            btn._icon_ref = icon

        return btn

    def create_toolbutton(self, parent, icon_name: str, text: str = "",
                         command=None, size: str = "small",
                         **kwargs) -> ttk.Button:
        """创建工具栏按钮（小尺寸）"""
        return self.create_button(
            parent, icon_name, text, command, size,
            style="Toolbutton", **kwargs
        )

    def _get_emoji_fallback(self, icon_name: str) -> str:
        """获取 emoji 回退"""
        emoji_map = {
            'settings': '⚙️',
            'formula': '📐',
            'table': '📊',
            'refresh': '🔄',
            'export': '📤',
            'import': '📥',
            'add': '➕',
            'minus': '➖',
            'delete': '🗑️',
            'save': '💾',
            'open': '📂',
            'new': '📄',
            'preview': '👁️',
            'help': '❓',
            'info': 'ℹ️',
            'camera': '📷',
            'copy': '📋',
            'search': '🔍',
            'folder': '📁',
            'file': '📄',
            'edit': '✏️',
            'close': '❌',
            'check': '✓',
            'download': '⬇️',
            'upload': '⬆️',
            'home': '🏠',
            'back': '←',
            'forward': '→',
            'up': '↑',
            'down': '↓',
            'list': '☰',
            'grid': '⊞',
            'more': '⋯',
            'menu': '☰',
        }
        return emoji_map.get(icon_name, '•')

    def set_button_icon(self, button: ttk.Button, icon_name: str,
                       size: Union[str, Tuple[int, int]] = "medium"):
        """为现有按钮设置图标"""
        icon = self.get_icon(icon_name, size)
        if icon:
            button.configure(image=icon)
            button._icon_ref = icon


# 全局实例
_icon_manager = None


def get_icon_manager() -> IconManager:
    """获取全局 IconManager 实例"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


def load_icon(icon_name: str, size: Union[str, Tuple[int, int]] = "medium",
              color: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
    """快捷函数：加载图标"""
    return get_icon_manager().get_icon(icon_name, size, color)
