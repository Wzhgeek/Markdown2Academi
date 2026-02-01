"""
主窗口 - 桌面端 GUI (tkinter)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading

from src.converters.markdown_to_docx import MarkdownToDocxConverter
from src.converters.formula_converter import FormulaConverter
from src.utils.config import Config


class MainWindow:
    """主应用窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Markdown to Academia v0.1.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # 配置
        self.config = Config()

        # 转换器
        self.docx_converter = MarkdownToDocxConverter()
        self.formula_converter = FormulaConverter(self.config.get('mathpix_app_id', ''),
                                                   self.config.get('mathpix_app_key', ''))

        # 当前文件
        self.current_file = None

        self._setup_ui()
        self._setup_menu()

    def _setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # ===== 文件选择区域 =====
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Markdown 文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        ttk.Button(file_frame, text="浏览", command=self._browse_file).grid(row=0, column=2, padx=5)
        ttk.Button(file_frame, text="新建", command=self._new_file).grid(row=0, column=3, padx=5)

        # 拖拽提示
        ttk.Label(file_frame, text="💡 提示: 支持拖拽文件到窗口", foreground="gray").grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

        # ===== 模板选择区域 =====
        template_frame = ttk.LabelFrame(main_frame, text="模板设置", padding="10")
        template_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(template_frame, text="选择模板:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.template_var = tk.StringVar(value="thesis")
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, state="readonly",
                                      values=["thesis", "journal", "custom"], width=20)
        template_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(template_frame, text="输出格式:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.output_format = tk.StringVar(value="docx")
        ttk.Combobox(template_frame, textvariable=self.output_format, state="readonly",
                     values=["docx", "pdf", "latex"], width=15).grid(row=0, column=3, sticky=tk.W, padx=5)

        # ===== 预览区域 =====
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=20)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.preview_text.insert(tk.END, "请选择或拖拽 Markdown 文件...")
        self.preview_text.config(state=tk.DISABLED)

        # ===== 按钮区域 =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="⚙️ 设置", command=self._open_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 公式识别", command=self._open_formula_tool).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 表格转换", command=self._open_table_tool).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="🔄 刷新预览", command=self._refresh_preview).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="📄 导出文档", command=self._export_document).pack(side=tk.RIGHT, padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        # 绑定拖拽事件
        self.root.drop_target_register("DND_Files")
        self.root.dnd_bind("<<Drop>>", self._on_drop)

    def _setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开", command=self._browse_file, accelerator="Ctrl+O")
        file_menu.add_command(label="新建", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="导出", command=self._export_document, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Alt+F4")

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="公式识别", command=self._open_formula_tool)
        tools_menu.add_command(label="表格转换", command=self._open_table_tool)
        tools_menu.add_separator()
        tools_menu.add_command(label="设置", command=self._open_settings)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

        # 绑定快捷键
        self.root.bind("<Control-o>", lambda e: self._browse_file())
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<Control-e>", lambda e: self._export_document())

    def _browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择 Markdown 文件",
            filetypes=[("Markdown files", "*.md *.markdown"), ("All files", "*.*")]
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path):
        """加载文件"""
        self.current_file = file_path
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)
        self._refresh_preview()
        self.status_var.set(f"已加载: {os.path.basename(file_path)}")

    def _new_file(self):
        """新建文件"""
        template = """---
title: 论文标题
author: 作者姓名
school: 学院名称
template: thesis
citation-style: gb7714
---

#abstract 中文摘要
在这里输入中文摘要...

#abstract-en Abstract
English abstract here...

#keywords 关键词1, 关键词2, 关键词3

# 第一章 绪论

## 1.1 研究背景

开始写作...

## 1.2 研究意义

...

# 参考文献

"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, template)
        self.preview_text.config(state=tk.NORMAL)
        self.current_file = None
        self.file_entry.delete(0, tk.END)
        self.status_var.set("新建文件 - 请保存后导出")

    def _on_drop(self, event):
        """处理文件拖拽"""
        file_path = event.data
        if file_path:
            # 移除花括号（某些平台拖拽会带花括号）
            file_path = file_path.strip("{}")
            if file_path.endswith(('.md', '.markdown')):
                self._load_file(file_path)
            else:
                messagebox.showwarning("不支持的文件", "请拖拽 Markdown 文件 (.md, .markdown)")

    def _refresh_preview(self):
        """刷新预览"""
        if not self.current_file:
            content = self.preview_text.get(1.0, tk.END)
            if content.strip() and content.strip() != "请选择或拖拽 Markdown 文件...":
                self.preview_text.config(state=tk.NORMAL)
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, content)
            self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件: {e}")

    def _export_document(self):
        """导出文档"""
        if not self.current_file:
            # 检查预览区是否有内容
            content = self.preview_text.get(1.0, tk.END)
            if not content.strip() or content.strip() == "请选择或拖拽 Markdown 文件...":
                messagebox.showwarning("提示", "请先打开或创建一个 Markdown 文件")
                return

            # 保存临时文件
            temp_file = os.path.join(os.path.expanduser("~"), ".markdown2academia_temp.md")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            input_file = temp_file
        else:
            input_file = self.current_file

        # 选择输出路径
        output_format = self.output_format.get()
        extensions = {"docx": ".docx", "pdf": ".pdf", "latex": ".tex"}
        default_ext = extensions.get(output_format, ".docx")

        output_file = filedialog.asksaveasfilename(
            title="保存文档",
            defaultextension=default_ext,
            filetypes=[
                (f"{output_format.upper()} files", f"*{default_ext}"),
                ("All files", "*.*")
            ]
        )

        if not output_file:
            return

        # 异步转换
        self.status_var.set("正在转换...")
        threading.Thread(target=self._do_export,
                         args=(input_file, output_file, output_format),
                         daemon=True).start()

    def _do_export(self, input_file, output_file, output_format):
        """执行导出"""
        try:
            template = self.template_var.get()
            self.docx_converter.convert(input_file, output_file, template=template)
            self.root.after(0, lambda: self._export_complete(output_file))
        except Exception as e:
            self.root.after(0, lambda: self._export_error(str(e)))

    def _export_complete(self, output_file):
        """导出完成"""
        self.status_var.set(f"导出成功: {output_file}")
        if messagebox.askyesno("成功", f"文档已导出到:\n{output_file}\n\n是否打开文件?"):
            self._open_file(output_file)

    def _export_error(self, error_msg):
        """导出错误"""
        self.status_var.set("导出失败")
        messagebox.showerror("转换错误", f"导出失败:\n{error_msg}")

    def _open_file(self, file_path):
        """打开文件"""
        import platform
        import subprocess

        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")

    def _open_settings(self):
        """打开设置对话框"""
        SettingsDialog(self.root, self.config)

    def _open_formula_tool(self):
        """打开公式识别工具"""
        FormulaDialog(self.root, self.formula_converter)

    def _open_table_tool(self):
        """打开表格转换工具"""
        messagebox.showinfo("提示", "表格转换功能开发中...")

    def _show_help(self):
        """显示帮助"""
        help_text = """
Markdown to Academia 使用说明

1. 打开文件: 点击"浏览"或拖拽 Markdown 文件到窗口
2. 选择模板: 根据需要选择论文模板或期刊模板
3. 预览: 实时预览 Markdown 内容
4. 导出: 点击"导出文档"生成 Word/PDF/LaTeX 文件

扩展语法:
- #abstract: 中文摘要
- #abstract-en: 英文摘要
- #keywords: 关键词
- #figure: 图片
- #table: 表格
- #equation: 公式
        """
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        """显示关于"""
        messagebox.showinfo("关于",
                            "Markdown to Academia v0.1.0\n\n"
                            "学术论文格式转换工具\n\n"
                            "基于 Pandoc 和 Python-docx 构建")

    def run(self):
        """运行应用"""
        self.root.mainloop()


class SettingsDialog:
    """设置对话框"""

    def __init__(self, parent, config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()
        self._load_settings()

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """设置界面"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Mathpix API 设置
        ttk.Label(frame, text="Mathpix API 设置", font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame, text="App ID:").pack(anchor=tk.W)
        self.app_id_entry = ttk.Entry(frame, width=50)
        self.app_id_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="App Key:").pack(anchor=tk.W)
        self.app_key_entry = ttk.Entry(frame, width=50, show="*")
        self.app_key_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(frame, text="测试连接", command=self._test_mathpix).pack(anchor=tk.W, pady=(0, 20))

        # 默认设置
        ttk.Label(frame, text="默认设置", font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame, text="默认模板:").pack(anchor=tk.W)
        self.default_template = ttk.Combobox(frame, values=["thesis", "journal", "custom"], state="readonly")
        self.default_template.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="默认输出格式:").pack(anchor=tk.W)
        self.default_format = ttk.Combobox(frame, values=["docx", "pdf", "latex"], state="readonly")
        self.default_format.pack(fill=tk.X, pady=(0, 20))

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="保存", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_settings(self):
        """加载设置"""
        self.app_id_entry.insert(0, self.config.get('mathpix_app_id', ''))
        self.app_key_entry.insert(0, self.config.get('mathpix_app_key', ''))
        self.default_template.set(self.config.get('default_template', 'thesis'))
        self.default_format.set(self.config.get('default_format', 'docx'))

    def _test_mathpix(self):
        """测试 Mathpix 连接"""
        from src.converters.formula_converter import FormulaConverter
        converter = FormulaConverter(self.app_id_entry.get(), self.app_key_entry.get())
        # 这里可以添加一个简单的测试调用
        messagebox.showinfo("提示", "请保存设置后使用公式识别功能测试")

    def _save(self):
        """保存设置"""
        self.config.set('mathpix_app_id', self.app_id_entry.get())
        self.config.set('mathpix_app_key', self.app_key_entry.get())
        self.config.set('default_template', self.default_template.get())
        self.config.set('default_format', self.default_format.get())
        self.config.save()
        self.dialog.destroy()
        messagebox.showinfo("成功", "设置已保存")


class FormulaDialog:
    """公式识别对话框"""

    def __init__(self, parent, converter):
        self.converter = converter
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("公式识别 (Mathpix)")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)

        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="公式截图识别", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 图片选择
        ttk.Label(frame, text="选择公式图片:").pack(anchor=tk.W)
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="浏览", command=self._browse_image).pack(side=tk.RIGHT)

        # 截图按钮
        ttk.Button(frame, text="📷 截图 (开发中)", state=tk.DISABLED).pack(anchor=tk.W, pady=(0, 10))

        # 识别按钮
        ttk.Button(frame, text="🔍 识别公式", command=self._recognize).pack(anchor=tk.W, pady=(0, 10))

        # 结果显示
        ttk.Label(frame, text="LaTeX 代码:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 复制按钮
        ttk.Button(frame, text="📋 复制到剪贴板", command=self._copy_to_clipboard).pack(anchor=tk.W)

    def _browse_image(self):
        """浏览图片"""
        file_path = filedialog.askopenfilename(
            title="选择公式图片",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def _recognize(self):
        """识别公式"""
        image_path = self.file_entry.get()
        if not image_path:
            messagebox.showwarning("提示", "请先选择公式图片")
            return

        try:
            latex = self.converter.image_to_latex(image_path)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, latex)
        except Exception as e:
            messagebox.showerror("错误", f"识别失败: {e}")

    def _copy_to_clipboard(self):
        """复制到剪贴板"""
        latex = self.result_text.get(1.0, tk.END).strip()
        if latex:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(latex)
            messagebox.showinfo("成功", "已复制到剪贴板")
