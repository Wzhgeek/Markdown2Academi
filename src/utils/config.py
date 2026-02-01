"""
配置管理工具
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """配置管理类"""

    CONFIG_FILE = "config.json"
    CONFIG_DIR = ".markdown2academia"

    def __init__(self):
        self.config_path = Path.home() / self.CONFIG_DIR / self.CONFIG_FILE
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load()

    def _load(self) -> dict:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value

    def delete(self, key: str):
        """删除配置项"""
        if key in self._config:
            del self._config[key]

    def get_mathpix_credentials(self) -> tuple:
        """获取 Mathpix API 凭证"""
        return (
            self.get('mathpix_app_id', ''),
            self.get('mathpix_app_key', '')
        )

    def set_mathpix_credentials(self, app_id: str, app_key: str):
        """设置 Mathpix API 凭证"""
        self.set('mathpix_app_id', app_id)
        self.set('mathpix_app_key', app_key)
        self.save()
