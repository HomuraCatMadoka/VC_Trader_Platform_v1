"""項目自定義異常。"""


class KArbError(Exception):
    """頂層異常，便於統一捕獲。"""


class GatewayError(KArbError):
    """網關通信異常。"""


class ParserError(KArbError):
    """數據解析異常。"""


class WrapperError(KArbError):
    """封裝層異常。"""


class ConfigError(KArbError):
    """配置讀取與驗證異常。"""
