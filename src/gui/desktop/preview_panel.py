"""
Markdown 实时渲染预览面板
支持富文本渲染和 HTML 显示
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import markdown
from markdown.extensions import fenced_code, tables, toc
import re


class PreviewPanel:
    """Markdown 预览面板"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        # 配置 frame 的 grid 权重，使其可以扩展
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # Markdown 转换器
        self.md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
        ])

        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 预览模式选择
        mode_frame = ttk.Frame(self.frame)
        mode_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(mode_frame, text="预览模式:").pack(side=tk.LEFT, padx=(0, 5))
        self.preview_mode = tk.StringVar(value="rich")
        ttk.Radiobutton(mode_frame, text="富文本", variable=self.preview_mode,
                        value="rich", command=self._switch_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="原始文本", variable=self.preview_mode,
                        value="raw", command=self._switch_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="HTML", variable=self.preview_mode,
                        value="html", command=self._switch_mode).pack(side=tk.LEFT, padx=5)

        # 内容区域
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 富文本预览
        self.rich_text = tk.Text(self.content_frame, wrap=tk.WORD, state=tk.DISABLED,
                                 bg='white', padx=10, pady=10)
        self.rich_text_scroll = ttk.Scrollbar(self.content_frame, command=self.rich_text.yview)
        self.rich_text.configure(yscrollcommand=self.rich_text_scroll.set)

        # 原始文本预览
        self.raw_text = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, state=tk.DISABLED)

        # HTML 预览
        self.html_text = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, state=tk.DISABLED,
                                                   font=('Courier', 10))

        # 显示当前模式
        self._switch_mode()

    def _switch_mode(self):
        """切换预览模式"""
        mode = self.preview_mode.get()

        # 隐藏所有
        self.rich_text.pack_forget()
        self.rich_text_scroll.pack_forget()
        self.raw_text.pack_forget()
        self.html_text.pack_forget()

        # 配置 content_frame 的 grid 权重
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # 显示选中模式
        if mode == "rich":
            self.rich_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.rich_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        elif mode == "raw":
            self.raw_text.pack(fill=tk.BOTH, expand=True)
        else:  # html
            self.html_text.pack(fill=tk.BOTH, expand=True)

    def update_preview(self, md_content: str, template: str = "thesis"):
        """
        更新预览内容

        Args:
            md_content: Markdown 内容
            template: 模板名称，影响渲染样式
        """
        mode = self.preview_mode.get()

        if mode == "raw":
            self._update_raw(md_content)
        elif mode == "html":
            self._update_html(md_content)
        else:
            self._update_rich(md_content, template)

    def _update_raw(self, content: str):
        """更新原始文本预览"""
        self.raw_text.config(state=tk.NORMAL)
        self.raw_text.delete(1.0, tk.END)
        self.raw_text.insert(tk.END, content)
        self.raw_text.config(state=tk.DISABLED)
        self.raw_text.update()  # 强制刷新显示

    def _update_html(self, content: str):
        """更新 HTML 预览"""
        self.md.reset()
        html = self.md.convert(content)

        self.html_text.config(state=tk.NORMAL)
        self.html_text.delete(1.0, tk.END)
        self.html_text.insert(tk.END, html)
        self.html_text.config(state=tk.DISABLED)
        self.html_text.update()  # 强制刷新显示

    def _update_rich(self, content: str, template: str):
        """更新富文本预览"""
        self.rich_text.config(state=tk.NORMAL)
        self.rich_text.delete(1.0, tk.END)

        # 解析并渲染 Markdown
        self._render_rich_text(content, template)

        self.rich_text.config(state=tk.DISABLED)
        self.rich_text.update()  # 强制刷新显示

    def _render_rich_text(self, content: str, template: str):
        """使用 tkinter Text 渲染富文本"""
        # 配置标签样式
        self._configure_tags(template)

        # 预处理扩展语法
        content = self._preprocess_extended_syntax(content)

        # 逐行解析和渲染
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]

            # 标题
            if line.startswith('# '):
                self._insert_heading(line[2:], 1)
            elif line.startswith('## '):
                self._insert_heading(line[3:], 2)
            elif line.startswith('### '):
                self._insert_heading(line[4:], 3)
            elif line.startswith('#### '):
                self._insert_heading(line[5:], 4)
            # 代码块
            elif line.startswith('```'):
                i = self._insert_code_block(lines, i)
                continue
            # 表格
            elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                i = self._insert_table(lines, i)
                continue
            # 列表
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                self._insert_bullet(line.strip()[2:])
            elif re.match(r'^\d+\.\s', line.strip()):
                self._insert_numbered(line.strip())
            # 普通段落
            elif line.strip():
                self._insert_paragraph(line)
            else:
                self.rich_text.insert(tk.END, '\n')

            i += 1

    def _configure_tags(self, template: str):
        """配置文本标签样式"""
        # 根据模板设置字体
        if template == "thesis":
            title_font = ('黑体', 16, 'bold')
            h1_font = ('黑体', 14, 'bold')
            h2_font = ('黑体', 12, 'bold')
            h3_font = ('黑体', 11, 'bold')
            body_font = ('宋体', 12)
        else:  # journal
            title_font = ('Times New Roman', 14, 'bold')
            h1_font = ('Times New Roman', 12, 'bold')
            h2_font = ('Times New Roman', 11, 'bold')
            h3_font = ('Times New Roman', 10, 'bold')
            body_font = ('Times New Roman', 10)

        self.rich_text.tag_configure('h1', font=h1_font, spacing3=10)
        self.rich_text.tag_configure('h2', font=h2_font, spacing3=8)
        self.rich_text.tag_configure('h3', font=h3_font, spacing3=6)
        self.rich_text.tag_configure('h4', font=body_font, underline=True)
        self.rich_text.tag_configure('bold', font=(body_font[0], body_font[1], 'bold'))
        self.rich_text.tag_configure('italic', font=(body_font[0], body_font[1], 'italic'))
        self.rich_text.tag_configure('code', font=('Courier', body_font[1]),
                                     background='#f0f0f0')
        self.rich_text.tag_configure('code_block', font=('Courier', body_font[1] - 1),
                                     background='#f5f5f5', spacing1=5, spacing3=5)
        self.rich_text.tag_configure('center', justify='center')
        self.rich_text.tag_configure('abstract_title', font=h1_font, justify='center')
        self.rich_text.tag_configure('abstract_content', font=body_font,
                                     spacing1=5, spacing3=5, lmargin1=20, lmargin2=20)
        self.rich_text.tag_configure('keywords', font=body_font, spacing3=10)
        self.rich_text.tag_configure('equation', font=('Courier', body_font[1] + 2),
                                     justify='center', spacing1=5, spacing3=5)

    def _preprocess_extended_syntax(self, content: str) -> str:
        """预处理扩展语法"""
        # 处理 #abstract
        content = re.sub(r'^#abstract\s*', '**摘要**\n\n', content, flags=re.MULTILINE)
        content = re.sub(r'^#abstract-en\s*', '**Abstract**\n\n', content, flags=re.MULTILINE)
        content = re.sub(r'^#keywords\s*', '**关键词：**', content, flags=re.MULTILINE)

        # 处理 #equation
        def replace_equation(match):
            eq = match.group(1).strip()
            return f"\n$$ {eq} $$\n"

        content = re.sub(r'^#equation\s+(.+?)(?:\s*\|\s*label=(.+))?$',
                         replace_equation, content, flags=re.MULTILINE)

        # 处理 #figure
        def replace_figure(match):
            caption = match.group(1)
            return f"\n**图:** {caption}\n"

        content = re.sub(r'^#figure\s+(.+?)\s*\|.+?$', replace_figure,
                         content, flags=re.MULTILINE)

        # 处理 #table
        def replace_table(match):
            caption = match.group(1)
            return f"\n**表:** {caption}\n"

        content = re.sub(r'^#table\s+(.+?)\s*\|.+?$', replace_table,
                         content, flags=re.MULTILINE)

        return content

    def _insert_heading(self, text: str, level: int):
        """插入标题"""
        tag = f'h{level}'
        self.rich_text.insert(tk.END, text + '\n', tag)
        self.rich_text.insert(tk.END, '\n')

    def _insert_paragraph(self, text: str):
        """插入段落（支持行内格式）"""
        # 处理行内格式
        self._insert_with_inline_format(text)
        self.rich_text.insert(tk.END, '\n\n')

    def _insert_with_inline_format(self, text: str):
        """插入带行内格式的文本"""
        # 解析粗体和斜体
        parts = re.split(r'(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)

        for part in parts:
            if part.startswith('***') and part.endswith('***'):
                # 粗斜体
                self.rich_text.insert(tk.END, part[3:-3], ('bold', 'italic'))
            elif part.startswith('**') and part.endswith('**'):
                # 粗体
                self.rich_text.insert(tk.END, part[2:-2], 'bold')
            elif part.startswith('*') and part.endswith('*'):
                # 斜体
                self.rich_text.insert(tk.END, part[1:-1], 'italic')
            elif part.startswith('`') and part.endswith('`'):
                # 行内代码
                self.rich_text.insert(tk.END, part[1:-1], 'code')
            else:
                self.rich_text.insert(tk.END, part)

    def _insert_code_block(self, lines: list, start_idx: int) -> int:
        """插入代码块，返回结束行索引"""
        lang = lines[start_idx][3:].strip()
        i = start_idx + 1
        code_lines = []

        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1

        code = '\n'.join(code_lines)
        self.rich_text.insert(tk.END, code + '\n', 'code_block')
        self.rich_text.insert(tk.END, '\n')

        return i + 1

    def _insert_table(self, lines: list, start_idx: int) -> int:
        """插入表格，返回结束行索引"""
        i = start_idx
        rows = []

        # 收集表格行
        while i < len(lines) and '|' in lines[i]:
            rows.append(lines[i])
            i += 1

        # 渲染表格（简化版）
        for j, row in enumerate(rows):
            if '---' in row:
                continue  # 跳过分隔线

            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            row_text = ' | '.join(cells)

            if j == 0:
                # 表头
                self.rich_text.insert(tk.END, row_text + '\n', 'bold')
                self.rich_text.insert(tk.END, '-' * len(row_text) + '\n')
            else:
                self.rich_text.insert(tk.END, row_text + '\n')

        self.rich_text.insert(tk.END, '\n')
        return i

    def _insert_bullet(self, text: str):
        """插入无序列表项"""
        self.rich_text.insert(tk.END, '• ')
        self._insert_with_inline_format(text)
        self.rich_text.insert(tk.END, '\n')

    def _insert_numbered(self, text: str):
        """插入有序列表项"""
        self._insert_with_inline_format(text)
        self.rich_text.insert(tk.END, '\n')

    def clear(self):
        """清空预览"""
        for widget in [self.rich_text, self.raw_text, self.html_text]:
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.config(state=tk.DISABLED)
