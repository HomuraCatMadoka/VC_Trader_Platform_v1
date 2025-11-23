"""日志工具，提供結構化輸出與統一配置。"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

DEFAULT_LOGGER_NAME = "k_arb"


def _format_record(record: logging.LogRecord) -> str:
    payload: Dict[str, Any] = {
        "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
        "level": record.levelname,
        "name": record.name,
        "message": record.getMessage(),
    }
    extra_keys = set(record.__dict__.keys()) - {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    }
    for key in extra_keys:
        payload[key] = record.__dict__[key]
    if record.exc_info:
        payload["exception"] = logging.Formatter().formatException(record.exc_info)
    return json.dumps(payload, ensure_ascii=False)


class JsonFormatter(logging.Formatter):
    """極簡 JSON 格式化器。"""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        return _format_record(record)


def setup_logger(name: str = DEFAULT_LOGGER_NAME, level: int = logging.INFO) -> logging.Logger:
    """初始化 logger（冪等）。"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger
