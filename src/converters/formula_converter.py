"""
公式转换器 - 使用 Mathpix API
"""

import base64
import requests
from typing import Optional


class FormulaConverter:
    """公式识别转换器"""

    MATHPIX_API_URL = "https://api.mathpix.com/v3/text"

    def __init__(self, app_id: str = "", app_key: str = ""):
        self.app_id = app_id
        self.app_key = app_key

    def is_configured(self) -> bool:
        """检查是否已配置 API 密钥"""
        return bool(self.app_id and self.app_key)

    def image_to_latex(self, image_path: str) -> str:
        """
        将图片中的公式转换为 LaTeX 代码

        Args:
            image_path: 图片文件路径

        Returns:
            LaTeX 代码字符串
        """
        if not self.is_configured():
            raise ValueError("Mathpix API 未配置，请在设置中配置 App ID 和 App Key")

        # 读取图片并转为 base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # 构建请求
        headers = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'Content-type': 'application/json'
        }

        data = {
            'src': f'data:image/png;base64,{image_data}',
            'formats': ['latex_styled', 'latex_simplified'],
            'include_ascii': True,
            'include_tsv': True,
        }

        # 发送请求
        response = requests.post(self.MATHPIX_API_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # 返回 LaTeX 代码
        latex = result.get('latex_styled', '')
        if not latex:
            latex = result.get('latex_simplified', '')

        return latex

    def image_to_latex_batch(self, image_paths: list) -> list:
        """
        批量转换图片公式

        Args:
            image_paths: 图片文件路径列表

        Returns:
            LaTeX 代码列表
        """
        results = []
        for path in image_paths:
            try:
                latex = self.image_to_latex(path)
                results.append(latex)
            except Exception as e:
                results.append(f"Error: {e}")
        return results

    def latex_to_mathml(self, latex: str) -> str:
        """
        将 LaTeX 转换为 MathML（用于 Word 兼容）

        Args:
            latex: LaTeX 代码

        Returns:
            MathML 字符串
        """
        # 这里可以使用其他库如 latex2mathml
        # 或者使用 Mathpix 的额外格式
        return f"<math><mi>LaTeX:</mi><mtext>{latex}</mtext></math>"

    def test_connection(self) -> bool:
        """测试 Mathpix API 连接"""
        if not self.is_configured():
            return False

        try:
            # 使用一个简单的测试图片
            test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

            headers = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'Content-type': 'application/json'
            }

            data = {
                'src': f'data:image/png;base64,{test_image}',
                'formats': ['text'],
            }

            response = requests.post(self.MATHPIX_API_URL, headers=headers, json=data)
            return response.status_code == 200

        except Exception:
            return False
