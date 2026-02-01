# Markdown to Academia

基于 Pandoc 的学术论文格式转换 GUI 工具，支持 Markdown 转 Word，并集成公式/表格转换功能。

## 功能特点

- ✍️ **Markdown 写作**：使用简洁的 Markdown 语法撰写论文
- 📄 **Word 输出**：一键导出符合学校/期刊格式的 Word 文档
- 🎓 **学术模板**：内置毕业论文、期刊论文模板
- 🔢 **公式识别**：集成 Mathpix API，截图转 LaTeX 公式
- 📊 **表格转换**：Excel/CSV 转 LaTeX/Markdown 表格
- 🖥️ **跨平台**：支持 Windows、macOS、Android

## 安装

### 依赖要求

- Python 3.8+
- Pandoc ([安装指南](https://pandoc.org/installing.html))

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Wzhgeek/Markdown2Academi.git
cd Markdown2Academi

# 安装依赖
pip install -r requirements-desktop.txt

# 运行
python main.py
```

## 使用方法

### 1. 编写 Markdown 文件

```markdown
---
title: 论文标题
author: 作者姓名
school: 学院名称
major: 专业
template: thesis
---

#abstract
这里是中文摘要内容...

#keywords 关键词1, 关键词2, 关键词3

# 第一章 绪论

## 1.1 研究背景

开始写作...

#equation E=mc^2

#figure 示例图片 | image.png | width=80%

#table 数据表格 | data.csv | header=true
```

### 2. 打开 GUI

运行 `python main.py`，选择 Markdown 文件或拖拽到窗口。

### 3. 选择模板

- `thesis`：毕业论文模板（含封面、页眉页脚）
- `journal`：期刊论文模板

### 4. 导出文档

点击「导出文档」按钮，选择保存位置，生成 Word 文件。

## 扩展语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `#abstract` | 中文摘要 | `#abstract 内容...` |
| `#abstract-en` | 英文摘要 | `#abstract-en Abstract...` |
| `#keywords` | 关键词 | `#keywords 关键词1, 关键词2` |
| `#figure` | 图片 | `#figure 标题 | path.png | width=80%` |
| `#table` | 表格 | `#table 标题 | data.csv | header=true` |
| `#equation` | 公式 | `#equation E=mc^2 | label=eq-1` |

## 平台支持

| 平台 | 状态 | 下载 |
|------|------|------|
| Windows | ✅ | [下载 EXE](https://github.com/Wzhgeek/Markdown2Academi/releases) |
| macOS (Intel) | ✅ | [下载 DMG](https://github.com/Wzhgeek/Markdown2Academi/releases) |
| macOS (Apple Silicon) | ✅ | [下载 DMG](https://github.com/Wzhgeek/Markdown2Academi/releases) |
| Android | 🚧 开发中 | - |

## 开发

### 项目结构

```
markdown-to-academia/
├── src/
│   ├── gui/            # GUI 界面
│   ├── converters/     # 转换器核心
│   ├── templates/      # 论文模板
│   └── utils/          # 工具函数
├── main.py             # 入口文件
├── requirements-desktop.txt
└── requirements-mobile.txt
```

### 构建

GitHub Actions 会在每次提交时自动构建各平台安装包。

## 许可证

MIT License

## 致谢

- [Pandoc](https://pandoc.org/) - 文档转换引擎
- [python-docx](https://python-docx.readthedocs.io/) - Word 处理
- [Mathpix](https://mathpix.com/) - 公式识别 API
