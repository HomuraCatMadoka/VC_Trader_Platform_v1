# Phase 2 多交易對 DryRun 使用與調試指南

## 1. 基本環境
- Python 3.11+
- 建議使用虛擬環境：`python -m venv .venv && source .venv/bin/activate`
- 安裝依賴：`pip install -r requirements.txt`（或 `uv pip sync requirements.txt`）

## 2. 配置說明
### 2.1 API 與交易對
- `config/development.yaml`：填入 Upbit/Bithumb 的 REST/WS URL 與 API Key。
- `config/pairs.yaml`：列出本輪重點監控的 `X/KRW` 交易對（已依照梯隊分組：搬磚之王 / 韓流熱點 / 泡菜幣）。腳本會自動轉成 Upbit `KRW-X` 與 Bithumb `X_KRW`，如需增刪只要編輯此檔即可。
  - 可用環境變數 `MAX_DRYRUN_PAIRS=<N>` 控制一次載入的交易對數量。
- 若 `pairs.yaml` 不存在，會回退到 `config.development.yaml` 裡的單一 `symbol_upbit/symbol_bithumb`。

### 2.2 日誌
- `config/development.yaml` 的 `logging.level` 決定輸出詳略；建議調成 `DEBUG` 以查看所有步驟。
- 日誌中常見欄位：
  - `pair`：交易對名稱（例如 `BTC`）。
  - `direction`：`upbit_sell` / `bithumb_sell`。
  - `spread`、`volume`、`symbol` 供排查。

## 3. 執行 DryRun
```bash
MAX_DRYRUN_PAIRS=20 python scripts/run_dryrun.py
```
- 腳本會：
  1. 為每個交易對建立 `OrderBookManager` 與 `OrderBookFeed`。
  2. 啟動 WebSocket，持續更新 Upbit/Bithumb 訂單簿。
  3. 於循環中對每個交易對計算 Spread → 風控 → DryRun 下單。
- 日誌範例：
  ```json
  {"level":"DEBUG","name":"dryrun_engine","message":"策略無有效信號","pair":"BTC"}
  {"level":"INFO","name":"dryrun_engine","message":"DryRun 交易完成","pair":"ETH","direction":"upbit_sell","volume":"0.05"}
  ```

## 4. 調試工具
### 4.1 `scripts/debug_dryrun.py`
單次檢查某組 Upbit/Bithumb 狀態：
```bash
python scripts/debug_dryrun.py
```
輸出包含：
- Upbit/Bithumb 前 5 檔買/賣深度
- 目前階段的 bid/ask 價格
- 所有餘額（可用/凍結）
- 是否產生策略信號、風控結果
- 若有信號，執行 DryRun 並顯示成功訊息

> 即使無信號也會繼續列出餘額與風控結論，方便確認 API 是否正常。

### 4.2 `scripts/analyze_profit_logs.py`
從 DryRun 日誌中統計有利潤的交易對：
```bash
python scripts/analyze_profit_logs.py dryrun.log
```
會輸出各交易對的成功次數、平均成交量、平均 spread，便於分析哪些交易對較常觸發信號。

## 5. 常見排查步驟
1. **策略無信號**：
   - 用 `debug_dryrun.py` 檢查當下 spread；若 Upbit/Bithumb 價差不大屬正常。
   - 調整 `StrategyConfig` 的 `min_profit_rate`、`max_volume` 或 `fee`。
2. **風控拒絕**：
   - 日誌會顯示 "風控拒絕信號"，查看 `reserve_ratio`、`PositionLimit` 是否過嚴。
   - 可在 `config` 中降低保留比例或提高限額。
3. **網路/DNS 問題**：
   - 若出現 `ClientConnectorDNSError`，先確認 `curl https://api.upbit.com/...` 可正常；在 Windows 環境上建議移除 `aiodns` 或設定自訂 DNS。
4. **WebSocket message 缺欄位**：
   - 已在 Upbit wrapper 中處理 `code`→`market` 的對應；若 Bithumb 仍有空資料，可檢查 REST 初始化是否成功。
5. **日誌太多**：
   - 可用 `LOG_LEVEL=INFO python scripts/run_dryrun.py` 控制輸出等級。

## 6. 下一步建議
- 長時間 DryRun（24h+），搜集 `DryRun 交易完成` 的資料，利用 `analyze_profit_logs.py` 找出高頻交易對。
- 若要切換到真實下單，把 `OrderExecutor(dry_run=True)` 改為 `False`，並加上更嚴的風控（降低 volume、提高 reserve）。
- 適時加上監控/告警，把成功訊號、風控結果寫入資料庫或視覺化報表。

如需支援更多調試功能（例如個別交易對的細節輸出、異常事件告警），可再提出需求。祝測試順利！
