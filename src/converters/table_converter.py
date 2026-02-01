"""
表格转换器 - Excel/CSV 与 LaTeX/Markdown 互转
"""

import csv
import re
from typing import List, Optional
from pathlib import Path


class TableConverter:
    """表格转换器"""

    @staticmethod
    def csv_to_latex(csv_path: str, caption: str = "", has_header: bool = True) -> str:
        """
        将 CSV 文件转换为 LaTeX 表格

        Args:
            csv_path: CSV 文件路径
            caption: 表格标题
            has_header: 是否有表头

        Returns:
            LaTeX 表格代码
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return ""

        num_cols = len(rows[0])

        # 构建 LaTeX 代码
        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        if caption:
            lines.append(f"\\caption{{{caption}}}")
        lines.append(f"\\begin{{tabular}}{{{'|'.join(['c'] * num_cols)}}}")
        lines.append("\\hline")

        for i, row in enumerate(rows):
            # 转义特殊字符
            escaped_row = [TableConverter._escape_latex(cell) for cell in row]
            lines.append(" & ".join(escaped_row) + " \\\\")

            if has_header and i == 0:
                lines.append("\\hline")

        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append("\\label{tab:" + TableConverter._to_label(caption) + "}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    @staticmethod
    def csv_to_markdown(csv_path: str, has_header: bool = True) -> str:
        """
        将 CSV 文件转换为 Markdown 表格

        Args:
            csv_path: CSV 文件路径
            has_header: 是否有表头

        Returns:
            Markdown 表格代码
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return ""

        lines = []

        # 表头
        header = rows[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        # 数据行
        start_idx = 1 if has_header else 0
        for row in rows[start_idx:]:
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    @staticmethod
    def excel_to_csv(excel_path: str, sheet_name: Optional[str] = None) -> str:
        """
        将 Excel 文件转换为 CSV

        Args:
            excel_path: Excel 文件路径
            sheet_name: 工作表名称

        Returns:
            CSV 文件路径
        """
        try:
            import pandas as pd

            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_path)

            # 转换为 CSV
            csv_path = excel_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8')
            return csv_path

        except ImportError:
            raise ImportError("请先安装 pandas: pip install pandas openpyxl")

    @staticmethod
    def latex_to_csv(latex_table: str) -> str:
        """
        从 LaTeX 表格中提取数据并转换为 CSV

        Args:
            latex_table: LaTeX 表格代码

        Returns:
            CSV 内容字符串
        """
        lines = []

        # 解析 tabular 环境
        tabular_match = re.search(r'\\begin{tabular}.*?}(.*?)\\end{tabular}', latex_table, re.DOTALL)
        if not tabular_match:
            return ""

        content = tabular_match.group(1)

        # 提取行
        for line in content.split('\\\\'):
            line = line.strip()
            if not line or line.startswith('\\hline'):
                continue

            # 分割单元格
            cells = [cell.strip() for cell in line.split('&')]
            lines.append(','.join(cells))

        return '\n'.join(lines)

    @staticmethod
    def _escape_latex(text: str) -> str:
        """转义 LaTeX 特殊字符"""
        special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }

        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)

        return text

    @staticmethod
    def _to_label(text: str) -> str:
        """将文本转换为有效的 LaTeX label"""
        label = re.sub(r'[^\w\s-]', '', text.lower())
        label = re.sub(r'[-\s]+', '-', label)
        return label[:50]
