# market-calendar-data

「重大事件」iOS App 的事件資料。App 每次打開會下載這裡的 `events.json`。

- `build_events.py`：事件清單（美國事件填美東時間，自動換算台灣時間），執行後產生 `events.json`
- `events.json`：App 讀取的資料，時間皆為台灣時間（ISO 8601，+08:00）
- `estimated: true` 表示日期依往年慣例推估，正式公告後會更新

更新方式：修改 `build_events.py` → `python3 build_events.py` → commit & push。
