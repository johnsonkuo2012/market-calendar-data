"""產生 events.json：美東時間的事件自動換算成台灣時間（含夏令/冬令時間切換）。"""
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
TW = ZoneInfo("Asia/Taipei")

events = []


def add(eid, title, category, when, *, importance=2, estimated=False,
        detail="", source="", all_day=False, tz=ET):
    if all_day:
        d = when if isinstance(when, date) else when.date()
        dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=TW)
    else:
        dt = when.replace(tzinfo=tz).astimezone(TW)
    events.append({
        "id": eid,
        "title": title,
        "category": category,
        "date": dt.isoformat(),
        "allDay": all_day,
        "importance": importance,
        "estimated": estimated,
        "detail": detail,
        "source": source,
    })


def third_weekday(year, month, weekday):  # weekday: Mon=0
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d + timedelta(weeks=2)


FED = "federalreserve.gov"
BLS = "bls.gov"
BEA = "bea.gov"

# ---------- 美國總經 ----------
for eid, d, sep in [
    ("fomc-2026-10", datetime(2026, 10, 28, 14, 0), False),
    ("fomc-2026-12", datetime(2026, 12, 9, 14, 0), True),
    ("fomc-2027-01", datetime(2027, 1, 27, 14, 0), False),
    ("fomc-2027-03", datetime(2027, 3, 17, 14, 0), True),
]:
    extra = "本次附經濟預測摘要（SEP）與點陣圖。" if sep else ""
    add(eid, "FOMC 利率決議", "usMacro", d, importance=3,
        detail=f"聯準會公布利率決策聲明，30 分鐘後主席召開記者會。{extra}",
        source=FED)

for eid, d, month in [
    ("cpi-2026-11", datetime(2026, 11, 10, 8, 30), "10 月"),
    ("cpi-2026-12", datetime(2026, 12, 10, 8, 30), "11 月"),
]:
    add(eid, f"美國 CPI（{month}）", "usMacro", d, importance=3,
        detail="消費者物價指數，影響市場對聯準會利率路徑的預期。", source=BLS)

for eid, d, month in [
    ("nfp-2026-11", datetime(2026, 11, 6, 8, 30), "10 月"),
    ("nfp-2026-12", datetime(2026, 12, 4, 8, 30), "11 月"),
    ("nfp-2027-01", datetime(2027, 1, 8, 8, 30), "12 月"),
    ("nfp-2027-02", datetime(2027, 2, 5, 8, 30), "1 月"),
]:
    add(eid, f"美國非農就業（{month}）", "usMacro", d, importance=3,
        detail="Employment Situation：非農新增就業、失業率、薪資成長。", source=BLS)

add("gdp-pce-2026-10", "美國 GDP 初值（Q3）＋ PCE（9 月）", "usMacro",
    datetime(2026, 10, 29, 8, 30), importance=2,
    detail="BEA 同時公布第三季 GDP 預估值與個人所得支出（含聯準會偏好的 PCE 物價指數）。",
    source=BEA)
add("gdp-pce-2026-11", "美國 GDP 修正值（Q3）＋ PCE（10 月）", "usMacro",
    datetime(2026, 11, 25, 8, 30), importance=2,
    detail="第三季 GDP 第二次估計與 10 月 PCE 物價指數。", source=BEA)
add("gdp-pce-2026-12", "美國 GDP 終值（Q3）＋ PCE（11 月）", "usMacro",
    datetime(2026, 12, 23, 8, 30), importance=2,
    detail="第三季 GDP 第三次估計與 11 月 PCE 物價指數。", source=BEA)

add("witching-2026-12", "美股四巫日", "usMacro",
    datetime.combine(third_weekday(2026, 12, 4), datetime.min.time()).replace(hour=16),
    importance=1,
    detail="股票、指數期貨與選擇權同日到期，收盤前後波動與成交量常放大。",
    source="依每季第三個週五推算")

# ---------- 台灣市場 ----------
add("tw-gdp-2026-q3", "台灣 Q3 GDP 概估", "twMarket",
    datetime(2026, 10, 30, 16, 0), tz=TW, importance=2, estimated=True,
    detail="主計總處公布第三季經濟成長率概估。往年多在 10 月最後一個工作日公布。",
    source="主計總處（依往年慣例推估）")
add("tw-forecast-2026-11", "主計總處經濟預測", "twMarket",
    datetime(2026, 11, 27, 16, 0), tz=TW, importance=2, estimated=True,
    detail="國民所得評審會，更新全年與明年經濟成長率、CPI 預測。往年多在 11 月底。",
    source="主計總處（依往年慣例推估）")
add("tw-cbc-2026-q4", "台灣央行理監事會（Q4）", "twMarket",
    datetime(2026, 12, 17, 16, 0), tz=TW, importance=3, estimated=True,
    detail="央行公布利率決策與房市信用管制，會後總裁記者會。往年多在 FOMC 後一週的週四召開，正式日期以央行公告為準。",
    source="中央銀行（依往年慣例推估）")

for y, m in [(2026, 11), (2026, 12), (2027, 1)]:
    d = third_weekday(y, m, 2)  # 第三個週三
    add(f"txf-settle-{y}-{m:02d}", f"台指期 {m} 月結算", "twMarket",
        datetime(d.year, d.month, d.day, 13, 30), tz=TW, importance=2,
        detail="台指期與台指選擇權月合約最後結算日（每月第三個週三），收盤前後常有結算行情。",
        source="依期交所規則推算")

for eid, d, month in [
    ("tsmc-rev-2026-11", datetime(2026, 11, 10, 13, 30), "10 月"),
    ("tsmc-rev-2026-12", datetime(2026, 12, 10, 13, 30), "11 月"),
    ("tsmc-rev-2027-01", datetime(2027, 1, 8, 13, 30), "12 月"),
]:
    add(eid, f"台積電 {month}營收", "twEarnings", d, tz=TW, importance=2, estimated=True,
        detail="台積電通常在每月 10 日前後盤後公布上月合併營收，正式日期以公司公告為準。",
        source="台積電（依往年慣例推估）")

add("tsmc-call-2027-01", "台積電 Q4 法說會", "twEarnings",
    datetime(2027, 1, 14, 14, 0), tz=TW, importance=3, estimated=True,
    detail="公布第四季財報、第一季財測與全年資本支出。往年多在 1 月中旬的週四，正式日期以公司公告為準。",
    source="台積電（依往年慣例推估）")

# ---------- 台股法說與財報 ----------
MOPS = "公開資訊觀測站／公司公告"
for eid, d, title, imp, detail in [
    ("umc-2026-q3", datetime(2026, 10, 28, 17, 0), "聯電 Q3 法說會", 2, "線上法說，公布第三季財報與第四季展望。"),
    ("shuanghong-2026-q3", datetime(2026, 10, 29, 9, 0), "雙鴻 Q3 法說會", 1, "散熱族群指標。"),
    ("auo-2026-q3", datetime(2026, 10, 29, 14, 0), "友達 Q3 法說會", 1, "面板族群指標。"),
    ("realtek-2026-q3", datetime(2026, 10, 29, 16, 0), "瑞昱 Q3 法說會", 2, "網通、PC 晶片需求風向。"),
    ("yageo-2026-q3", datetime(2026, 10, 29, 16, 0), "國巨 Q3 法說會", 2, "被動元件龍頭。"),
    ("liteon-2026-q3", datetime(2026, 10, 30, 14, 0), "光寶科 Q3 法說會", 1, "電源、AI 伺服器電源供應。"),
    ("mtk-2026-q3", datetime(2026, 10, 30, 15, 0), "聯發科 Q3 法說會", 3, "線上法說，公布第三季財報與第四季財測，台股第二大權值股之一。"),
]:
    add(eid, title, "twEarnings", d, tz=TW, importance=imp, detail=detail, source=MOPS)

add("delta-2026-q3", "台達電 Q3 法說會", "twEarnings",
    datetime(2026, 10, 29, 14, 0), tz=TW, importance=2, estimated=True,
    detail="AI 伺服器電源、散熱指標股。法說日期已公布，時間未查到確切公告，這裡先標 14:00。",
    source="新聞報導")
add("honhai-techday-2026", "鴻海科技日", "twEarnings",
    datetime(2026, 10, 30, 10, 0), tz=TW, importance=2,
    detail="鴻海第七屆科技日（10/30–10/31，南港展覽館一館），市場關注 AI 伺服器、電動車與機器人布局。",
    source="鴻海")
add("honhai-2026-q3", "鴻海 Q3 法說會", "twEarnings",
    datetime(2026, 11, 12, 14, 0), tz=TW, importance=3, estimated=True,
    detail="去年第三季法說在 11/12 舉行，今年日期以公司公告為準。市場聚焦 AI 伺服器出貨與第四季展望。",
    source="鴻海（依往年慣例推估）")

for eid, d, month in [
    ("rev-deadline-2026-11", date(2026, 11, 10), "10 月"),
    ("rev-deadline-2026-12", date(2026, 12, 10), "11 月"),
    ("rev-deadline-2027-01", date(2027, 1, 11), "12 月"),
]:
    add(eid, f"月營收公布期限（{month}）", "twEarnings", d, all_day=True, importance=1,
        detail="上市櫃公司須在每月 10 日前公布上月營收（遇假日順延），多數公司會提前在月初陸續公布。",
        source="證交所規定")

add("q3-deadline-2026", "上市櫃 Q3 財報公告截止", "twEarnings", date(2026, 11, 14), all_day=True,
    importance=2,
    detail="一般上市櫃公司須在 11/14 前公告第三季財報（11/14 為週六，多數公司會在 11/13 前公布）；金控、銀行等金融業期限稍晚。",
    source="證交所規定")

add("msci-review-2026-11", "MSCI 季度調整公布", "twMarket",
    datetime(2026, 11, 12, 6, 0), tz=TW, importance=2, estimated=True,
    detail="MSCI 公布 11 月季度指數調整結果（美東 11/11 公布，台灣約 11/12 清晨），包含台股權重與成分股增刪。",
    source="MSCI")
add("msci-effective-2026-11", "MSCI 調整生效（尾盤換股）", "twMarket",
    datetime(2026, 11, 30, 13, 30), tz=TW, importance=2,
    detail="MSCI 11 月調整於 12/1 生效，被動資金在 11/30 收盤前換股，台股尾盤常出現爆量。",
    source="MSCI")

# ---------- 美股財報 ----------
add("msft-2026-10", "微軟財報（FY27 Q1）", "earnings",
    datetime(2026, 10, 28, 16, 0), importance=2,
    detail="美股盤後公布，市場聚焦 Azure 雲端成長與 AI 資本支出。", source="Microsoft IR")
add("googl-2026-10", "Alphabet 財報（Q3）", "earnings",
    datetime(2026, 10, 28, 16, 0), importance=2,
    detail="美股盤後公布，聚焦 Google Cloud 與 AI 資本支出。", source="Alphabet IR")
add("amzn-2026-10", "Amazon 財報（Q3）", "earnings",
    datetime(2026, 10, 29, 16, 0), importance=2,
    detail="美股盤後公布，聚焦 AWS 成長。", source="Amazon IR")
add("aapl-2026-11", "Apple 財報（FY26 Q4）", "earnings",
    datetime(2026, 11, 2, 16, 30), importance=2,
    detail="美股盤後公布，17:00（美東）法說會，含 iPhone 18 Pro 首週銷售。", source="Apple IR")
add("nvda-2026-11", "輝達財報（FY27 Q3）", "earnings",
    datetime(2026, 11, 18, 16, 20), importance=3, estimated=True,
    detail="AI 供應鏈最關鍵的財報之一，對台股電子權值影響大。公司尚未正式公告日期。",
    source="市場預估（依往年慣例）")

# ---------- 休市日 ----------
for eid, d, title, detail in [
    ("us-thanks-2026", date(2026, 11, 26), "美股休市：感恩節", "紐約證交所與那斯達克全日休市。"),
    ("us-blackfri-2026", date(2026, 11, 27), "美股提早收盤", "感恩節翌日，美股於美東 13:00 提早收盤。"),
    ("us-xmaseve-2026", date(2026, 12, 24), "美股提早收盤", "聖誕夜，美股於美東 13:00 提早收盤。"),
    ("us-xmas-2026", date(2026, 12, 25), "美股休市：聖誕節", "美股全日休市。"),
    ("us-ny-2027", date(2027, 1, 1), "美股休市：元旦", "美股全日休市。"),
    ("us-mlk-2027", date(2027, 1, 18), "美股休市：馬丁路德金紀念日", "美股全日休市。"),
]:
    add(eid, title, "holiday", d, all_day=True, importance=1, detail=detail, source="NYSE")

for eid, d, title in [
    ("tw-const-2026", date(2026, 12, 25), "台股休市：行憲紀念日"),
    ("tw-ny-2027", date(2027, 1, 1), "台股休市：元旦"),
]:
    add(eid, title, "holiday", d, all_day=True, importance=1,
        detail="台股集中市場休市。", source="臺灣證券交易所")

events.sort(key=lambda e: e["date"])
import sys
# 預設寫到 App 專案內；也可指定輸出路徑：python3 build_events.py path/to/events.json
here = Path(__file__).resolve().parent
default_out = here / "MarketCalendar" / "events.json" if (here / "MarketCalendar").is_dir() else here / "events.json"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else default_out
with open(out, "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

for e in events:
    flag = "（預估）" if e["estimated"] else ""
    print(e["date"][:16].replace("T", " "), e["title"], flag)
print(len(events), "events")
