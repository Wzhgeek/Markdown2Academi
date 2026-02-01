"""
表格编辑器 - 可视化编辑表格数据
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import io

from src.gui.desktop.icon_manager import get_icon_manager


class TableEditor:
    """表格编辑器对话框"""

    def __init__(self, parent, converter):
        self.converter = converter
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("表格编辑器")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 表格数据
        self.headers = ["列1", "列2", "列3"]
        self.data = [["", "", ""]]

        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 初始化图标管理器
        self.icon_manager = get_icon_manager()

        # 工具栏
        toolbar = ttk.Frame(self.dialog)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        self.icon_manager.create_button(toolbar, icon_name="add", text="添加行",
                                        command=self._add_row, size="small").pack(side=tk.LEFT, padx=2)
        self.icon_manager.create_button(toolbar, icon_name="minus", text="删除行",
                                        command=self._remove_row, size="small").pack(side=tk.LEFT, padx=2)
        self.icon_manager.create_button(toolbar, icon_name="add", text="添加列",
                                        command=self._add_col, size="small").pack(side=tk.LEFT, padx=2)
        self.icon_manager.create_button(toolbar, icon_name="minus", text="删除列",
                                        command=self._remove_col, size="small").pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.icon_manager.create_button(toolbar, icon_name="upload", text="导入 CSV",
                                        command=self._import_csv, size="small").pack(side=tk.LEFT, padx=2)
        self.icon_manager.create_button(toolbar, icon_name="download", text="导出",
                                        command=self._show_export_dialog, size="small").pack(side=tk.LEFT, padx=2)

        # 表格区域
        table_frame = ttk.Frame(self.dialog)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建 Treeview
        self.tree = ttk.Treeview(table_frame, columns=self.headers, show='headings')
        self._update_tree_columns()

        # 滚动条
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # 绑定双击编辑
        self.tree.bind('<Double-1>', self._on_double_click)

        # 按钮区域
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="清空", command=self._clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _update_tree_columns(self):
        """更新表格列"""
        # 清空现有列
        for col in self.tree['columns']:
            self.tree.heading(col, text='')

        self.tree['columns'] = self.headers
        for col in self.headers:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # 刷新数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.data:
            self.tree.insert('', tk.END, values=row)

    def _add_row(self):
        """添加行"""
        new_row = [""] * len(self.headers)
        self.data.append(new_row)
        self.tree.insert('', tk.END, values=new_row)

    def _remove_row(self):
        """删除选中行"""
        selected = self.tree.selection()
        if selected:
            for item in selected:
                idx = self.tree.index(item)
                self.data.pop(idx)
                self.tree.delete(item)

    def _add_col(self):
        """添加列"""
        new_col = f"列{len(self.headers) + 1}"
        self.headers.append(new_col)
        for row in self.data:
            row.append("")
        self._update_tree_columns()

    def _remove_col(self):
        """删除最后一列"""
        if len(self.headers) > 1:
            self.headers.pop()
            for row in self.data:
                if row:
                    row.pop()
            self._update_tree_columns()

    def _on_double_click(self, event):
        """双击编辑单元格"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)

        if not item:
            return

        col_idx = int(column[1:]) - 1
        x, y, width, height = self.tree.bbox(item, column)

        # 获取当前值
        values = list(self.tree.item(item, 'values'))
        current_value = values[col_idx] if col_idx < len(values) else ""

        # 创建编辑框
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            entry.destroy()

            # 更新数据
            row_idx = self.tree.index(item)
            if row_idx < len(self.data) and col_idx < len(self.data[row_idx]):
                self.data[row_idx][col_idx] = new_value

            # 更新显示
            values[col_idx] = new_value
            self.tree.item(item, values=values)

        def cancel_edit(event=None):
            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Escape>', cancel_edit)

    def _import_csv(self):
        """导入 CSV 文件"""
        file_path = filedialog.askopenfilename(
            title="选择 CSV 文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if rows:
                self.headers = rows[0]
                self.data = rows[1:] if len(rows) > 1 else []
                self._update_tree_columns()

            messagebox.showinfo("成功", f"已导入 {len(self.data)} 行数据")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    def _show_export_dialog(self):
        """显示导出对话框"""
        dialog = tk.Toplevel(self.dialog)
        dialog.title("导出表格")
        dialog.geometry("400x250")
        dialog.transient(self.dialog)
        dialog.grab_set()

        ttk.Label(dialog, text="选择导出格式:").pack(pady=10)

        format_var = tk.StringVar(value="latex")
        ttk.Radiobutton(dialog, text="LaTeX 表格", variable=format_var, value="latex").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(dialog, text="Markdown 表格", variable=format_var, value="markdown").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(dialog, text="CSV 文件", variable=format_var, value="csv").pack(anchor=tk.W, padx=20)

        caption_var = tk.StringVar(value="表格标题")
        ttk.Label(dialog, text="表格标题:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=caption_var).pack(fill=tk.X, padx=20)

        def do_export():
            fmt = format_var.get()
            caption = caption_var.get()

            if fmt == "latex":
                content = self._export_latex(caption)
                ext = ".tex"
            elif fmt == "markdown":
                content = self._export_markdown(caption)
                ext = ".md"
            else:
                content = self._export_csv()
                ext = ".csv"

            file_path = filedialog.asksaveasfilename(
                title="保存文件",
                defaultextension=ext,
                filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")]
            )

            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("成功", f"已导出到: {file_path}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"导出失败: {e}")

        ttk.Button(dialog, text="导出", command=do_export).pack(pady=20)

    def _export_latex(self, caption: str) -> str:
        """导出为 LaTeX"""
        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        lines.append(f"\\caption{{{caption}}}")

        col_format = "c" * len(self.headers)
        lines.append(f"\\begin{{tabular}}{{{'|'.join(col_format)}}}")
        lines.append("\\hline")

        # 表头
        lines.append(" & ".join(self.headers) + " \\\\")
        lines.append("\\hline")

        # 数据
        for row in self.data:
            escaped = [self._escape_latex(cell) for cell in row]
            lines.append(" & ".join(escaped) + " \\\\")

        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append("\\label{tab:" + caption.replace(' ', '_') + "}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    def _export_markdown(self, caption: str) -> str:
        """导出为 Markdown"""
        lines = []

        # 表头
        lines.append("| " + " | ".join(self.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")

        # 数据
        for row in self.data:
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")
        lines.append(f"*{caption}*")

        return "\n".join(lines)

    def _export_csv(self) -> str:
        """导出为 CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.headers)
        writer.writerows(self.data)
        return output.getvalue()

    def _escape_latex(self, text: str) -> str:
        """转义 LaTeX 特殊字符"""
        special = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
                   '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
                   '^': r'\textasciicircum{}'}
        for char, replacement in special.items():
            text = text.replace(char, replacement)
        return text

    def _clear(self):
        """清空表格"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗?"):
            self.headers = ["列1", "列2", "列3"]
            self.data = [["", "", ""]]
            self._update_tree_columns()
