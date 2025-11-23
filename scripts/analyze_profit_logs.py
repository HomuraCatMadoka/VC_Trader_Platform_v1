"""統計 DryRun 日誌中有利潤的交易。"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="統計 DryRun 日誌中的盈利訊號")
    parser.add_argument("logfile", type=Path, help="包含 JSON 日誌的檔案")
    args = parser.parse_args()

    counts = defaultdict(int)
    volume_sum = defaultdict(Decimal)
    spread_sum = defaultdict(Decimal)

    with args.logfile.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("message") != "DryRun 交易完成":
                continue
            pair = record.get("pair") or record.get("symbol") or "unknown"
            counts[pair] += 1
            if "volume" in record:
                try:
                    volume_sum[pair] += Decimal(str(record["volume"]))
                except Exception:
                    pass
            if "spread" in record:
                try:
                    spread_sum[pair] += Decimal(str(record["spread"]))
                except Exception:
                    pass

    if not counts:
        print("尚未在日誌中發現盈利記錄。")
        return

    print("=== 盈利統計 ===")
    for pair, cnt in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        avg_volume = (volume_sum[pair] / cnt) if volume_sum[pair] else Decimal("0")
        avg_spread = (spread_sum[pair] / cnt) if spread_sum[pair] else Decimal("0")
        print(f"{pair}: {cnt} 次，平均成交量 {avg_volume}, 平均 spread {avg_spread}")


if __name__ == "__main__":
    main()
