"""
LaTeX 导出器 - 支持中文，解决乱码问题
"""

import os
import re
from typing import Dict, Any, Optional


class LatexExporter:
    """LaTeX 导出器"""

    def __init__(self):
        self.templates = {
            "thesis": ThesisLatexTemplate(),
            "journal": JournalLatexTemplate(),
        }

    def export(self, md_content: str, output_file: str, template: str = "thesis",
               metadata: Optional[Dict[str, Any]] = None):
        """
        导出 Markdown 为 LaTeX 文件

        Args:
            md_content: Markdown 内容
            output_file: 输出 LaTeX 文件路径
            template: 模板名称
            metadata: 元数据
        """
        # 提取元数据
        if metadata is None:
            metadata = self._extract_metadata(md_content)

        # 预处理 Markdown 扩展语法
        latex_content = self._convert_to_latex(md_content, metadata)

        # 应用模板
        template_handler = self.templates.get(template, ThesisLatexTemplate())
        full_latex = template_handler.wrap(latex_content, metadata)

        # 写入文件（使用 UTF-8 编码）
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_latex)

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """提取 YAML 元数据"""
        metadata = {}
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")

        return metadata

    def _convert_to_latex(self, content: str, metadata: Dict[str, Any]) -> str:
        """将 Markdown 转换为 LaTeX"""
        # 移除 YAML 元数据
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        # 处理 #abstract
        content = re.sub(r'^#abstract\s*\n', r'\begin{abstract}\n', content, flags=re.MULTILINE)
        content = re.sub(r'^#abstract-en\s*\n', r'\begin{abstract-en}\n', content, flags=re.MULTILINE)

        # 处理 #keywords
        content = re.sub(r'^#keywords\s*(.+)$',
                         r'\\textbf{关键词：}\1', content, flags=re.MULTILINE)

        # 处理标题
        content = re.sub(r'^# (.+)$', r'\chapter{\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'\section{\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'\subsection{\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)$', r'\subsubsection{\1}', content, flags=re.MULTILINE)

        # 处理公式
        content = self._process_equations(content)

        # 处理图片
        content = self._process_figures(content)

        # 处理表格
        content = self._process_tables(content)

        # 处理粗体和斜体
        content = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', content)
        content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
        content = re.sub(r'\*(.+?)\*', r'\\textit{\1}', content)

        # 处理行内代码
        content = re.sub(r'`([^`]+)`', r'\\texttt{\1}', content)

        # 处理代码块
        content = re.sub(r'```(\w+)?\n(.*?)```',
                         lambda m: self._process_code_block(m.group(2), m.group(1)),
                         content, flags=re.DOTALL)

        # 处理列表
        content = self._process_lists(content)

        # 处理引用
        content = re.sub(r'^\[\d+\]\s*(.+)$',
                         r'\\bibitem{item} \1', content, flags=re.MULTILINE)

        # 处理换行
        content = re.sub(r'\n\n+', '\n\n', content)

        # 转义特殊字符
        content = self._escape_latex(content)

        return content.strip()

    def _process_equations(self, content: str) -> str:
        """处理公式"""
        # 处理 #equation
        def replace_equation(match):
            eq = match.group(1).strip()
            label = match.group(2)
            if label:
                return f'\\begin{{equation}}\n{eq}\n\\label{{{label}}}\n\\end{{equation}}'
            return f'\\begin{{equation}}\n{eq}\n\\end{{equation}}'

        content = re.sub(r'^#equation\s+(.+?)(?:\s*\|\s*label=(\S+))?\s*$',
                         replace_equation, content, flags=re.MULTILINE)

        # 处理行内公式 $...$
        content = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', content)

        # 处理块级公式 $$...$$
        content = re.sub(r'\$\$(.+?)\$\$', r'\\[\1\\]', content, flags=re.DOTALL)

        return content

    def _process_figures(self, content: str) -> str:
        """处理图片"""
        def replace_figure(match):
            caption = match.group(1).strip()
            image_path = match.group(2).strip()
            options = match.group(3) or ""

            width = "0.8"
            if "width=" in options:
                width_match = re.search(r'width=(\d+)%', options)
                if width_match:
                    width = int(width_match.group(1)) / 100

            return f'''\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width={width}\\textwidth]{{{image_path}}}
\\caption{{{caption}}}
\\end{{figure}}'''

        content = re.sub(r'^#figure\s+(.+?)\s*\|\s*(.+?)\s*(?:\|\s*(.+))?$',
                         replace_figure, content, flags=re.MULTILINE)

        # 处理标准 Markdown 图片 ![alt](path)
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
                         r'\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=0.8\\textwidth]{\2}\n\\caption{\1}\n\\end{figure}',
                         content)

        return content

    def _process_tables(self, content: str) -> str:
        """处理表格"""
        def replace_table(match):
            caption = match.group(1).strip()
            # 这里简化处理，实际应该读取 CSV 并生成表格
            return f'% 表格: {caption}\n% 请手动插入表格数据'

        content = re.sub(r'^#table\s+(.+?)\s*\|.+?$',
                         replace_table, content, flags=re.MULTILINE)

        return content

    def _process_code_block(self, code: str, language: Optional[str] = None) -> str:
        """处理代码块"""
        lang = language or "text"
        return f'\\begin{{lstlisting}}[language={lang}]\n{code}\\end{{lstlisting}}'

    def _process_lists(self, content: str) -> str:
        """处理列表"""
        lines = content.split('\n')
        result = []
        in_itemize = False
        in_enumerate = False

        for line in lines:
            # 无序列表
            if re.match(r'^[\s]*[-*]\s+', line):
                if not in_itemize:
                    if in_enumerate:
                        result.append('\\end{enumerate}')
                        in_enumerate = False
                    result.append('\\begin{itemize}')
                    in_itemize = True
                item_text = re.sub(r'^[\s]*[-*]\s+', '', line)
                result.append(f'\\item {item_text}')

            # 有序列表
            elif re.match(r'^[\s]*\d+\.\s+', line):
                if not in_enumerate:
                    if in_itemize:
                        result.append('\\end{itemize}')
                        in_itemize = False
                    result.append('\\begin{enumerate}')
                    in_enumerate = True
                item_text = re.sub(r'^[\s]*\d+\.\s+', '', line)
                result.append(f'\\item {item_text}')

            else:
                if in_itemize:
                    result.append('\\end{itemize}')
                    in_itemize = False
                if in_enumerate:
                    result.append('\\end{enumerate}')
                    in_enumerate = False
                result.append(line)

        if in_itemize:
            result.append('\\end{itemize}')
        if in_enumerate:
            result.append('\\end{enumerate}')

        return '\n'.join(result)

    def _escape_latex(self, text: str) -> str:
        """转义 LaTeX 特殊字符"""
        # 注意：不要转义已经在 LaTeX 命令中的字符
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
        }

        # 简单的替换，实际应该更复杂地处理
        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)

        return text


class LatexTemplate:
    """LaTeX 模板基类"""

    def wrap(self, content: str, metadata: Dict[str, Any]) -> str:
        """包装内容"""
        raise NotImplementedError


class ThesisLatexTemplate(LatexTemplate):
    """毕业论文 LaTeX 模板（中文支持）"""

    def wrap(self, content: str, metadata: Dict[str, Any]) -> str:
        title = metadata.get('title', '论文标题')
        author = metadata.get('author', '作者')
        school = metadata.get('school', '')
        date = metadata.get('date', '\\today')

        return f"""% !TEX encoding = UTF-8 Unicode
\\documentclass[12pt,a4paper]{{ctexart}}

% 中文支持
\\usepackage{{ctex}}

% 页面设置
\\usepackage{{geometry}}
\\geometry{{top=2.5cm,bottom=2.5cm,left=3cm,right=3cm}}

% 数学支持
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsthm}}

% 图片支持
\\usepackage{{graphicx}}
\\graphicspath{{{{./}}{{./figures/}}{{./images/}}}}

% 表格支持
\\usepackage{{booktabs}}
\\usepackage{{multirow}}

% 代码支持
\\usepackage{{listings}}
\\usepackage{{xcolor}}

% 超链接
\\usepackage{{hyperref}}
\\hypersetup{{colorlinks=true,linkcolor=black,citecolor=black}}

% 参考文献
\\usepackage{{biblatex}}

% 列表设置
\\usepackage{{enumitem}}

% 页眉页脚
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{{school}}}
\\fancyfoot[C]{{\\thepage}}

% 标题格式
\\ctexset{{
    section = {{
        format = \\zihao{{-3}}\\heiti\\centering,
    }},
    subsection = {{
        format = \\zihao{{4}}\\heiti,
    }},
    subsubsection = {{
        format = \\zihao{{-4}}\\heiti,
    }}
}}

% 代码样式
\\lstset{{
    language=Python,
    basicstyle=\\small\\ttfamily,
    keywordstyle=\\color{{blue}},
    commentstyle=\\color{{gray}},
    stringstyle=\\color{{red}},
    breaklines=true,
    frame=single,
}}

% 摘要环境
\\newenvironment{{abstract-en}}{{
    \\begin{{center}}
    \\textbf{{Abstract}}
    \\end{{center}}
    \\addcontentsline{{toc}}{{section}}{{Abstract}}
}}{{
    \\par
}}

\\title{{\\zihao{{2}}\\heiti {title}}}
\\author{{\\kaishu {author}}}
\\date{{{date}}}

\\begin{{document}}

% 封面
\\maketitle

% 摘要
{content}

% 参考文献（如果存在）
% \\printbibliography

\\end{{document}}
"""


class JournalLatexTemplate(LatexTemplate):
    """期刊论文 LaTeX 模板"""

    def wrap(self, content: str, metadata: Dict[str, Any]) -> str:
        title = metadata.get('title', '论文标题')
        author = metadata.get('author', '作者')

        return f"""% !TEX encoding = UTF-8 Unicode
\\documentclass[10pt,a4paper]{{article}}

% 中文支持
\\usepackage{{ctex}}

% 页面设置
\\usepackage{{geometry}}
\\geometry{{top=2cm,bottom=2cm,left=2.5cm,right=2.5cm}}

% 数学支持
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}

% 图片支持
\\usepackage{{graphicx}}

% 双倍行距（期刊常用）
\\usepackage{{setspace}}
\\doublespacing

% 其他包
\\usepackage{{hyperref}}
\\usepackage{{biblatex}}

\\title{{{title}}}
\\author{{{author}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
% 请在此处添加摘要
\\end{{abstract}}

{content}

\\end{{document}}
""
