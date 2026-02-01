#!/usr/bin/env python3
"""
Markdown to Academia - 学术论文格式转换工具
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="markdown-to-academia",
    version="0.1.0",
    author="Markdown2Academia Team",
    author_email="",
    description="基于 Pandoc 的学术论文格式转换工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Wzhgeek/Markdown2Academi",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pypandoc>=1.11",
        "python-docx>=0.8.11",
        "Pillow>=9.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "android": [
            "kivy>=2.2.0",
            "plyer>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "markdown2academia=main:main",
        ],
    },
)
