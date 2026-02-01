"""
Markdown2Academia - Android 移动端入口
基于 Kivy 框架
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


class Markdown2AcademiaApp(App):
    """主应用类"""

    def build(self):
        """构建 UI"""
        Window.clearcolor = (0.95, 0.95, 0.95, 1)

        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 标题
        title = Label(
            text='Markdown2Academia',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            color=(0.2, 0.2, 0.2, 1)
        )
        self.root.add_widget(title)

        # 文件选择按钮
        self.file_btn = Button(
            text='选择 Markdown 文件',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.file_btn.bind(on_press=self.show_file_chooser)
        self.root.add_widget(self.file_btn)

        # 选中的文件路径
        self.file_label = Label(
            text='未选择文件',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.root.add_widget(self.file_label)

        # 内容预览
        preview_label = Label(
            text='Markdown 预览:',
            size_hint_y=None,
            height=30,
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        preview_label.bind(size=lambda s, w: setattr(s, 'text_size', w))
        self.root.add_widget(preview_label)

        self.preview_input = TextInput(
            multiline=True,
            readonly=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            font_size='14sp'
        )
        self.root.add_widget(self.preview_input)

        # 转换按钮
        convert_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

        self.docx_btn = Button(
            text='导出 Word',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.docx_btn.bind(on_press=lambda x: self.convert('docx'))
        convert_box.add_widget(self.docx_btn)

        self.latex_btn = Button(
            text='导出 LaTeX',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.latex_btn.bind(on_press=lambda x: self.convert('latex'))
        convert_box.add_widget(self.latex_btn)

        self.root.add_widget(convert_box)

        # 状态标签
        self.status_label = Label(
            text='就绪',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.root.add_widget(self.status_label)

        self.selected_file = None

        return self.root

    def show_file_chooser(self, instance):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical')

        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.md', '*.txt']
        )
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=50)

        select_btn = Button(text='选择')
        cancel_btn = Button(text='取消')

        popup = Popup(title='选择 Markdown 文件', content=content, size_hint=(0.9, 0.9))

        def on_select(instance):
            if filechooser.selection:
                self.selected_file = filechooser.selection[0]
                self.file_label.text = os.path.basename(self.selected_file)
                self.load_file()
                popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_box.add_widget(select_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup.open()

    def load_file(self):
        """加载文件内容"""
        if self.selected_file and os.path.exists(self.selected_file):
            try:
                with open(self.selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.preview_input.text = content
                self.status_label.text = f'已加载: {os.path.basename(self.selected_file)}'
            except Exception as e:
                self.status_label.text = f'加载失败: {str(e)}'

    def convert(self, output_format):
        """转换文件"""
        if not self.selected_file:
            self.status_label.text = '请先选择文件'
            return

        content = self.preview_input.text
        if not content.strip():
            self.status_label.text = '内容为空'
            return

        try:
            from src.converters.markdown_to_docx import MarkdownToDocxConverter
            from src.converters.latex_exporter import LatexExporter

            output_dir = os.path.dirname(self.selected_file) or '.'
            base_name = os.path.splitext(os.path.basename(self.selected_file))[0]

            if output_format == 'docx':
                output_file = os.path.join(output_dir, f'{base_name}.docx')
                converter = MarkdownToDocxConverter()
                # 创建临时 md 文件
                temp_md = os.path.join(output_dir, f'_{base_name}_temp.md')
                with open(temp_md, 'w', encoding='utf-8') as f:
                    f.write(content)
                try:
                    converter.convert(temp_md, output_file, template='thesis')
                    self.status_label.text = f'Word 导出成功: {output_file}'
                finally:
                    if os.path.exists(temp_md):
                        os.unlink(temp_md)

            elif output_format == 'latex':
                output_file = os.path.join(output_dir, f'{base_name}.tex')
                exporter = LatexExporter()
                exporter.export(content, output_file, template='thesis')
                self.status_label.text = f'LaTeX 导出成功: {output_file}'

        except Exception as e:
            self.status_label.text = f'转换失败: {str(e)}'


def main():
    """主入口"""
    Markdown2AcademiaApp().run()


if __name__ == '__main__':
    main()
