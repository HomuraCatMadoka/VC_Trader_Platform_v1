# Phase 0 - API 訪問驗證計劃

## 目標
- 使用 aiohttp 驗證 Upbit 與 Bithumb 公共 REST API 是否可用
- 待取得 API Key 後，增加私有接口連通性

## 測試腳本
`scripts/verify_api_access.py`（待實作）將包含：
1. `test_upbit_public()`：GET `/v1/ticker?markets=KRW-BTC`
2. `test_bithumb_public()`：GET `/public/ticker/BTC_KRW`
3. 私有接口（計劃中）：GET `/v1/accounts`、`/info/balance`

## 待完成事項
- [ ] 編寫腳本與異常處理
- [ ] 申請並配置 API Key（僅查詢權限）
- [ ] 在 Phase 0 驗收前附上執行輸出

## 已知阻塞
- 目前執行 `python scripts/verify_api_access.py` 時遭遇 `SSL: CERTIFICATE_VERIFY_FAILED`，推測為本地系統缺少根憑證。
- 待在宿主機跑一次 `Install Certificates.command` 或手動指定 `certifi` CA 之後再重試。
