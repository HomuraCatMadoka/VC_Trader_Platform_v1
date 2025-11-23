"""配置讀取工具，封裝 YAML 解析與驗證。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

from core.exceptions import ConfigError

DEFAULT_CONFIG_PATH = Path("config/development.yaml")


class ConfigLoader:
    """簡單的 YAML 配置讀取器。"""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path or DEFAULT_CONFIG_PATH)

    def load(self) -> Dict[str, Any]:
        """讀取配置文件並返回字典。"""
        if not self._path.exists():
            raise ConfigError(f"配置文件不存在: {self._path}")

        try:
            content = self._path.read_text(encoding="utf-8")
            data = yaml.safe_load(content) or {}
            if not isinstance(data, dict):
                raise ConfigError("配置文件頂層必須是字典")
            return data
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigError(f"讀取配置文件失敗: {exc}") from exc


@lru_cache(maxsize=4)
def get_config(path: str | None = None) -> Dict[str, Any]:
    """獲取配置，默認讀取 development 環境。"""
    loader = ConfigLoader(Path(path) if path else None)
    return loader.load()
