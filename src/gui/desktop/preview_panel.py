"""
Markdown 实时渲染预览面板
左右分栏：左边编辑 Markdown，右边实时预览
"""

import tkinter as tk
from tkinter import ttk
import re


class PreviewPanel:
    """Markdown 预览面板 - 左右分栏"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # 配置 frame 的 grid 权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 当前模板
        self.current_template = "thesis"

        self._setup_ui()

    def _setup_ui(self):
        """设置界面 - 左右分栏"""
        # 使用 PanedWindow 实现可拖拽分栏
        self.paned = tk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.paned.grid(row=0, column=0, sticky="nsew")

        # ===== 左侧：Markdown 编辑器 =====
        left_frame = ttk.LabelFrame(self.paned, text="Markdown 源码")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        self.source_text = tk.Text(
            left_frame,
            wrap=tk.WORD,
            font=('Monaco', 11) if self._is_macos() else ('Consolas', 10),
            bg='#fafafa',
            fg='#333333',
            padx=10,
            pady=10,
            undo=True,
            maxundo=-1
        )
        self.source_text.grid(row=0, column=0, sticky="nsew")

        # 滚动条
        source_scroll = ttk.Scrollbar(left_frame, command=self.source_text.yview)
        source_scroll.grid(row=0, column=1, sticky="ns")
        self.source_text.configure(yscrollcommand=source_scroll.set)

        # ===== 右侧：渲染预览 =====
        right_frame = ttk.LabelFrame(self.paned, text="实时预览")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 根据系统和模板设置字体
        if self._is_macos():
            preview_font = ('PingFang SC', 12)  # macOS 使用苹方字体
        else:
            preview_font = ('Microsoft YaHei', 11)  # Windows 使用微软雅黑

        self.preview_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='white',
            padx=10,
            pady=10,
            cursor='arrow',
            font=preview_font
        )
        self.preview_text.grid(row=0, column=0, sticky="nsew")

        # 滚动条
        preview_scroll = ttk.Scrollbar(right_frame, command=self.preview_text.yview)
        preview_scroll.grid(row=0, column=1, sticky="ns")
        self.preview_text.configure(yscrollcommand=preview_scroll.set)

        # 添加到 PanedWindow
        self.paned.add(left_frame, minsize=300)
        self.paned.add(right_frame, minsize=300)

        # 设置默认分割比例
        self.paned.sash_place(0, 450, 0)

        # 绑定编辑事件 - 使用 after 延迟更新避免频繁刷新
        self._update_pending = None
        self.source_text.bind('<KeyRelease>', self._schedule_update)
        self.source_text.bind('<ButtonRelease>', self._schedule_update)

    def _is_macos(self) -> bool:
        """检测是否为 macOS"""
        import platform
        return platform.system() == 'Darwin'

    def _schedule_update(self, event=None):
        """延迟更新预览"""
        if self._update_pending:
            self.frame.after_cancel(self._update_pending)
        self._update_pending = self.frame.after(100, self._update_preview)

    def update_preview(self, md_content: str, template: str = "thesis"):
        """
        更新预览内容

        Args:
            md_content: Markdown 内容
            template: 模板名称，影响渲染样式
        """
        self.current_template = template

        # 更新左侧源码
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, md_content)

        # 强制立即更新右侧预览
        self.frame.update_idletasks()
        self._update_preview()

    def _update_preview(self):
        """更新右侧渲染预览"""
        content = self.source_text.get(1.0, tk.END).strip()

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if content and content != "请选择或拖拽 Markdown 文件...":
            # 渲染 Markdown
            self._render_markdown(content, self.current_template)
        else:
            self.preview_text.insert(tk.END, "请在左侧编辑 Markdown 内容...", 'body')

        self.preview_text.config(state=tk.DISABLED)

    def _render_markdown(self, content: str, template: str):
        """渲染 Markdown 为富文本"""
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
                self.preview_text.insert(tk.END, '\n')

            i += 1

    def _configure_tags(self, template: str):
        """配置文本标签样式"""
        # 根据系统和模板设置字体
        if self._is_macos():
            # macOS 字体
            if template == "thesis":
                h1_font = ('PingFang SC', 18, 'bold')
                h2_font = ('PingFang SC', 15, 'bold')
                h3_font = ('PingFang SC', 13, 'bold')
                h4_font = ('PingFang SC', 12, 'bold')
                body_font = ('PingFang SC', 12)
            else:  # journal
                h1_font = ('Times New Roman', 14, 'bold')
                h2_font = ('Times New Roman', 12, 'bold')
                h3_font = ('Times New Roman', 11, 'bold')
                h4_font = ('Times New Roman', 11, 'bold')
                body_font = ('Times New Roman', 11)
        else:
            # Windows/Linux 字体
            if template == "thesis":
                h1_font = ('Microsoft YaHei', 16, 'bold')
                h2_font = ('Microsoft YaHei', 14, 'bold')
                h3_font = ('Microsoft YaHei', 12, 'bold')
                h4_font = ('Microsoft YaHei', 11, 'bold')
                body_font = ('Microsoft YaHei', 11)
            else:  # journal
                h1_font = ('Times New Roman', 14, 'bold')
                h2_font = ('Times New Roman', 12, 'bold')
                h3_font = ('Times New Roman', 11, 'bold')
                h4_font = ('Times New Roman', 11, 'bold')
                body_font = ('Times New Roman', 11)

        # 配置文本颜色
        text_color = '#333333'

        self.preview_text.tag_configure('h1', font=h1_font, spacing3=10, foreground=text_color)
        self.preview_text.tag_configure('h2', font=h2_font, spacing3=8, foreground=text_color)
        self.preview_text.tag_configure('h3', font=h3_font, spacing3=6, foreground=text_color)
        self.preview_text.tag_configure('h4', font=h4_font, spacing3=4, foreground=text_color)
        self.preview_text.tag_configure('body', font=body_font, foreground=text_color)
        self.preview_text.tag_configure('bold', font=(body_font[0], body_font[1], 'bold'), foreground=text_color)
        self.preview_text.tag_configure('italic', font=(body_font[0], body_font[1], 'italic'), foreground=text_color)
        self.preview_text.tag_configure('code', font=('Courier', body_font[1]),
                                        background='#f0f0f0', foreground=text_color)
        self.preview_text.tag_configure('code_block', font=('Courier', body_font[1] - 1),
                                        background='#f5f5f5', spacing1=5, spacing3=5, foreground=text_color)
        self.preview_text.tag_configure('center', justify='center', foreground=text_color)
        self.preview_text.tag_configure('bullet', font=body_font, foreground=text_color)
        self.preview_text.tag_configure('numbered', font=body_font, foreground=text_color)

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
        self.preview_text.insert(tk.END, text + '\n', tag)
        self.preview_text.insert(tk.END, '\n')

    def _insert_paragraph(self, text: str):
        """插入段落（支持行内格式）"""
        self._insert_with_inline_format(text, 'body')
        self.preview_text.insert(tk.END, '\n\n', 'body')

    def _insert_with_inline_format(self, text: str, default_tag: str = 'body'):
        """插入带行内格式的文本"""
        # 解析粗体和斜体
        parts = re.split(r'(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)

        for part in parts:
            if part.startswith('***') and part.endswith('***'):
                self.preview_text.insert(tk.END, part[3:-3], ('bold', 'italic'))
            elif part.startswith('**') and part.endswith('**'):
                self.preview_text.insert(tk.END, part[2:-2], 'bold')
            elif part.startswith('*') and part.endswith('*'):
                self.preview_text.insert(tk.END, part[1:-1], 'italic')
            elif part.startswith('`') and part.endswith('`'):
                self.preview_text.insert(tk.END, part[1:-1], 'code')
            else:
                self.preview_text.insert(tk.END, part, default_tag)

    def _insert_code_block(self, lines: list, start_idx: int) -> int:
        """插入代码块"""
        i = start_idx + 1
        code_lines = []

        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1

        code = '\n'.join(code_lines)
        self.preview_text.insert(tk.END, code + '\n', 'code_block')
        self.preview_text.insert(tk.END, '\n', 'body')

        return i + 1

    def _insert_table(self, lines: list, start_idx: int) -> int:
        """插入表格"""
        i = start_idx
        rows = []

        while i < len(lines) and '|' in lines[i]:
            rows.append(lines[i])
            i += 1

        for j, row in enumerate(rows):
            if '---' in row:
                continue

            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            row_text = ' | '.join(cells)

            if j == 0:
                self.preview_text.insert(tk.END, row_text + '\n', 'bold')
                self.preview_text.insert(tk.END, '-' * len(row_text) + '\n', 'body')
            else:
                self.preview_text.insert(tk.END, row_text + '\n', 'body')

        self.preview_text.insert(tk.END, '\n', 'body')
        return i

    def _insert_bullet(self, text: str):
        """插入无序列表项"""
        self.preview_text.insert(tk.END, '• ', 'bullet')
        self._insert_with_inline_format(text, 'bullet')
        self.preview_text.insert(tk.END, '\n', 'bullet')

    def _insert_numbered(self, text: str):
        """插入有序列表项"""
        self._insert_with_inline_format(text, 'numbered')
        self.preview_text.insert(tk.END, '\n', 'numbered')

    def get_content(self) -> str:
        """获取当前 Markdown 内容"""
        return self.source_text.get(1.0, tk.END)

    def clear(self):
        """清空预览"""
        self.source_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
