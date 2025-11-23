# Phase 0 - 環境搭建記錄

## 1. 系統與語言版本
- macOS (按 Codex CLI 默認環境)
- Python: `python3 --version` → **3.13.7**

> 備註：官方建議 3.11+，實際環境使用 3.13，與項目需求兼容。

## 2. 虛擬環境
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 基礎依賴
```bash
.venv/bin/pip install aiohttp msgspec pyyaml
```

`requirements.txt` 已同步記錄版本：
- aiohttp 3.13.2
- msgspec 0.19.0
- PyYAML 6.0.3

## 4. 驗證項目入口
```bash
.venv/bin/python main.py
```
啟動後輸出 JSON 日誌（Hello K-Arb）。

## 5. 待辦
- 申請 Upbit/Bithumb API Key 並配置到環境變數
- 待 Phase 0 Day2 完成 API 連通性驗證腳本
