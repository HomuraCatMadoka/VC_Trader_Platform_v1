# Phase 2 使用與測試流程

## 一、環境與依賴準備
1. 安裝/確認 Python 3.11 以上版本。
2. 建立並啟動虛擬環境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   .\.venv\Scripts\activate        # Windows
   ```
3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   # 或者使用 uv：uv pip sync requirements.txt
   ```
   - 若使用 `uv`，如出現 `pluggy`、`multidict` 等缺失訊息，按提示再執行 `uv pip install <依賴>`。

## 二、配置 API Key
1. 編輯 `config/development.yaml`（或其他配置檔）填入交易所 REST/WS URL 與 API Key：
   ```yaml
   exchanges:
     upbit:
       rest_base: "https://api.upbit.com"
       websocket_url: "wss://api.upbit.com/websocket/v1"
       access_key: "<UPBIT_ACCESS_KEY>"
       secret_key: "<UPBIT_SECRET_KEY>"
     bithumb:
       rest_base: "https://api.bithumb.com"
       websocket_url: "wss://pubwss.bithumb.com/pub/ws"
       access_key: "<BITHUMB_ACCESS_KEY>"
       secret_key: "<BITHUMB_SECRET_KEY>"
   trading:
     symbol_upbit: "KRW-BTC"
     symbol_bithumb: "BTC_KRW"
     min_profit_rate: 0.005
   ```
2. 建議僅開交易權限、禁止提現；可將 Key 寫入環境變數後在 YAML 中引用。

## 三、單元測試（無需 API Key）
確保依賴與模組正常，執行：
```bash
pytest tests/unit/core/test_parser_upbit.py \
       tests/unit/core/test_parser_bithumb.py \
       tests/unit/core/test_wrapper_upbit.py \
       tests/unit/core/test_wrapper_bithumb.py \
       tests/unit/business/test_orderbook_manager.py \
       tests/unit/business/test_orderbook_feed.py \
       tests/unit/business/test_spread_strategy.py \
       tests/unit/business/test_risk_manager.py \
       tests/unit/business/test_order_executor.py \
       tests/unit/business/test_dryrun_engine.py
```
全部通過即代表 Phase 2 所有模塊就緒。

## 四、DryRun 流程（需 API、實際網路）
1. 確認配置檔中已填入有效 API Key/Secret，且可連線 Upbit/Bithumb。
2. 執行腳本：
   ```bash
   python scripts/run_dryrun.py
   ```
   腳本將：
   - 初始化 Upbit/Bithumb Gateway/Wrapper。
   - 啟動 `OrderBookFeed`（WebSocket）。
   - 持續進行「訂單簿快照 → Spread 策略 → RiskManager → OrderExecutor (DryRun)」循環。
3. 觀察日誌（終端或 logger 輸出），DryRun 成功會看到 `{"message":"DryRun 交易完成", ...}`，失敗則會有 warning。
4. 建議至少運行數小時，待行情/風控/執行流程穩定後再進行 24 小時 DryRun 驗證。

## 五、真實下單（可選）
1. 若 DryRun 表現良好，可將 `OrderExecutor(dry_run=True)` 改為 `False`，並確保風控配置更嚴格（降低 `max_volume`、增加 reserve）。
2. 使用極小資金先行測試，並保留日誌以供追蹤。
3. 所有真實測試需在工作環境自行進行；此步驟我不會執行。

## 六、修改指南（常用調整點）
| 修改內容 | 文件/模組 | 說明 |
| --- | --- | --- |
| API/交易對/策略門檻 | `config/development.yaml` | 調整 `exchanges`, `trading` 等配置即可。 |
| Gateway/限流 | `core/gateway(base.py, ratelimit/*.py)` | 新增交易所或調整限速器。 |
| Parser/Wrapper | `core/parser/*.py`, `core/wrapper/*.py` | 需變更字段或 API 行為時修改。 |
| 策略邏輯 | `business/strategy/spread_arbitrage.py` | 調整Spread計算、門檻、volume；或新增策略。 |
| 風控 | `business/risk/*.py` | 可調整 `reserve_ratio`、`PositionLimit`、`CircuitBreaker`。 |
| 執行方式 | `business/execution/executor.py` | 控制 DryRun / 實單、下單順序與類型。 |
| OrderBook 管理 | `business/orderbook/*.py` | 更新快照/增量邏輯、WS Feed。 |
| 主流程 | `business/engine/dryrun.py`, `scripts/run_dryrun.py` | 調整輪詢、掛載 feed、策略/風控/Executor 實例化方式。 |

> 所有現有測試（含 `scripts/run_dryrun.py`）默認為 DryRun，不會提交真實訂單；進入真單前，務必手動將 DryRun 參數改為 `False` 並仔細檢查風控與資金配置。

