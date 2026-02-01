# 图标资源目录

本目录包含应用程序使用的图标文件。

## 图标来源

图标来自 [Heroicons](https://heroicons.com/) - 由 Tailwind Labs 提供的开源 SVG 图标库。

## 当前图标列表

| 文件名 | 用途 |
|--------|------|
| settings.svg | 设置按钮 |
| table.svg | 表格转换 |
| export.svg | 导出文档 |
| refresh.svg | 刷新预览 |
| formula.svg | 公式识别 (calculator) |
| add.svg | 添加行/列 |
| minus.svg | 删除行/列 |
| upload.svg | 导入 CSV |
| download.svg | 导出文件 |
| folder-open.svg | 打开文件夹 |
| file-addition.svg | 新建文件 |
| preview.svg | 预览 |
| delete.svg | 删除 |
| help.svg | 帮助 |
| info.svg | 信息 |
| camera.svg | 相机/截图 |
| copy.svg | 复制 |
| search.svg | 搜索 |
| home.svg | 主页 |
| close.svg | 关闭 |
| check.svg | 确认 |
| menu.svg | 菜单 |

## 添加新图标

### 方法 1: 从 Heroicons 下载

```bash
# 进入图标目录
cd assets/icons

# 下载单个图标 (替换 icon-name 为实际图标名)
curl -sL "https://raw.githubusercontent.com/tailwindlabs/heroicons/master/src/24/outline/icon-name.svg" -o icon-name.svg
```

### 方法 2: 批量下载

编辑 `download_icons.py` 脚本，添加需要的图标名称，然后运行：

```bash
python download_icons.py
```

### 方法 3: 手动下载

1. 访问 https://heroicons.com/
2. 搜索需要的图标
3. 选择 "Outline" 风格
4. 下载 SVG 格式
5. 保存到 `assets/icons/` 目录

## 图标使用

在代码中使用图标：

```python
from src.gui.desktop.icon_manager import get_icon_manager

icon_manager = get_icon_manager()

# 创建带图标的按钮
button = icon_manager.create_button(
    parent, icon_name="settings", text="设置",
    command=callback, size="small"
)

# 仅图标
button = icon_manager.create_button(
    parent, icon_name="refresh",
    command=callback, size="medium"
)

# 手动加载图标
icon = icon_manager.get_icon("table", size="large")
```

## 图标尺寸

- `small`: 16x16 - 工具栏小按钮
- `medium`: 24x24 - 标准工具栏按钮 (默认)
- `large`: 32x32 - 大按钮/高 DPI
- `xlarge`: 48x48 - 超大按钮

## 颜色主题

图标默认为深色 (#333333)，可在加载时自定义颜色：

```python
# 使用蓝色图标
icon = icon_manager.get_icon("settings", color="#0066cc")
```

## 依赖

图标管理器需要以下依赖：

```bash
pip install pillow cairosvg
```

如果 CairoSVG 不可用，将自动回退到 PNG 格式或 Emoji。
