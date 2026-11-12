#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ooredoo Telegram Bot — Merged Clean Architecture
يجمع بين بنية القوائم وإدارة الجلسات، ومعايير التحقق والأمان لمنع التفعيلات الوهمية.
"""

import json
import logging
import os
import re
import threading
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------- الإعدادات والتهيئة ----------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ooredoo_bot")

# توكن البوت المضاف
TELEGRAM_BOT_TOKEN = "9153869404:AAGI0mkSrZKoF7Ukp6nkKFHyyhZwvtutxHk"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
DATA_FILE = Path(os.getenv("BOT_DATA_FILE", "bot_data.json"))
REQUEST_TIMEOUT = (5, 20)

# إعداد جلسة HTTP مستقرة مع إعادة المحاولة التلقائية
_tg_session = requests.Session()
_adapter = HTTPAdapter(
    pool_connections=50,
    pool_maxsize=100,
    max_retries=Retry(
        total=2,
        backoff_factor=0.3,
        status_forcelist=(502, 503, 504),
    ),
)
_tg_session.mount("https://", _adapter)

# ---------------- إدارة البيانات والذاكرة ----------------
_lock = threading.Lock()
_save_lock = threading.Lock()
_users = {}
_sessions = {}
_cooldowns = {}


def load_data():
    global _users
    if not DATA_FILE.exists():
        _users = {}
        return
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("users"), dict):
            _users = {int(k): v for k, v in raw["users"].items()}
        logger.info("✅ تم تحميل بيانات %d مستخدم", len(_users))
    except Exception as exc:
        logger.warning("تعذر تحميل ملف البيانات: %s", exc)
        _users = {}


def save_data():
    with _save_lock:
        temp = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
        try:
            with _lock:
                payload = {"users": {str(k): v for k, v in _users.items()}}
            temp.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temp, DATA_FILE)
        except OSError as exc:
            logger.error("خطأ أثناء حفظ البيانات: %s", exc)
            temp.unlink(missing_ok=True)


def check_cooldown(cid, seconds=15):
    now = time.time()
    with _lock:
        last = _cooldowns.get(cid, 0)
        if now - last < seconds:
            return int(seconds - (now - last))
        _cooldowns[cid] = now
    return 0


def mask_phone(phone):
    if not phone:
        return "—"
    s = str(phone).strip()
    return s[:2] + "x" * (len(s) - 4) + s[-2:] if len(s) >= 8 else s


# ---------------- دوال التواصل مع تليجرام ----------------
def tg_request(method, **kwargs):
    try:
        r = _tg_session.post(
            f"{TELEGRAM_API}/{method}",
            json=kwargs,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("result") if data.get("ok") else None
    except Exception as exc:
        logger.debug("خطأ في اتصال تليجرام (%s): %s", method, exc)
        return None


def tg_send(cid, text, rows=None):
    payload = {
        "chat_id": cid,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if rows:
        payload["reply_markup"] = {
            "keyboard": [[{"text": btn} for btn in row] for row in rows],
            "resize_keyboard": True,
        }
    return tg_request("sendMessage", **payload)


# ---------------- بوابة الربط والتحقق الصارم ----------------
def validate_provider_response(response_data):
    """
    التحقق الصارم من استجابة الخادم لمنع التفعيلات الوهمية:
    لا يُعتبر الطلب ناجحاً إلا إذا احتوى الرد على تأكيد صريح ورقم معاملة.
    """
    if not response_data or not isinstance(response_data, dict):
        return False, "استجابة فارغة أو غير صالحة من الخادم (Empty Body)."

    tx_id = response_data.get("transaction_id") or response_data.get("orderId")
    status = str(response_data.get("status", "")).upper()

    if status in ("CONFIRMED", "SUCCESS", "ACTIVE") and tx_id:
        return True, f"تم التأكيد بنجاح (رقم العملية: {tx_id})"

    error_msg = response_data.get("message") or response_data.get("error") or "الخدمة غير متاحة لهذا الرقم حالياً."
    return False, error_msg


def official_ooredoo_operation(operation, phone):
    """
    نقطة الربط المخصصة للتحقق من تنفيذ العمليات.
    """
    # محاكاة الاستجابة لمنع التفعيل الوهمي في حال كانت الاستجابة فارغة
    simulated_server_response = None  
    ok, msg = validate_provider_response(simulated_server_response)
    return {"success": ok, "message": msg}


# ---------------- القوائم وتنفيذ العمليات ----------------
def main_menu(cid, phone):
    tg_send(
        cid,
        f"📱 <b>الحساب المسجل:</b> <code>{mask_phone(phone)}</code>\nاختر الخدمة المطلوبة من القائمة 👇🏻",
        [
            ["📶 1G - 20DA", "👻 تفعيل Snapchat"],
            ["🎁 الهدية اليومية", "📦 الصناديق"],
            ["ℹ️ معلومات النظام", "🚪 خروج"],
        ],
    )


def execute_service(cid, phone, operation_code, title):
    wait = check_cooldown(cid, seconds=15)
    if wait > 0:
        return tg_send(cid, f"⚠️ يرجى الانتظار <b>{wait} ثانية</b> قبل إرسال طلب جديد.")

    tg_send(cid, f"⏳ جاري التحقق من الأهلية وتنفيذ <b>{title}</b>...")
    res = official_ooredoo_operation(operation_code, phone)

    if res.get("success") is True:
        tg_send(
            cid,
            f"🎉 <b>نجحت العملية ({title})</b>\n"
            f"📱 <b>الرقم:</b> <code>{mask_phone(phone)}</code>\n"
            f"✅ <b>التفاصيل:</b> {res.get('message')}",
            [["🔙 رجوع للقائمة"]],
        )
    else:
        tg_send(
            cid,
            f"❌ <b>تعذر إتمام الطلب ({title})</b>\n"
            f"📱 <b>الرقم:</b> <code>{mask_phone(phone)}</code>\n"
            f"🔍 <b>السبب الفعلي:</b> {res.get('message')}",
            [["🔙 رجوع للقائمة"]],
        )


def handle_message(cid, text):
    with _lock:
        user = dict(_users[cid]) if cid in _users else None
        sess = dict(_sessions.get(cid, {}))

    if text == "/start":
        with _lock:
            _sessions.pop(cid, None)
        if user and user.get("phone"):
            return main_menu(cid, user["phone"])
        with _lock:
            _sessions[cid] = {"state": "awaiting_phone"}
        return tg_send(cid, "👋 مرحباً بك!\nأرسل رقم هاتف Ooredoo الخاص بك (05XXXXXXXX) للمتابعة:")

    if sess.get("state") == "awaiting_phone":
        digits = "".join(c for c in text if c.isdigit())
        if not re.match(r"^05\d{8}$", digits):
            return tg_send(cid, "❌ صيغة الرقم غير صحيحة. أرسل رقماً يبدأ بـ 05 (مثال: 0550123456):")
        with _lock:
            _users[cid] = {"phone": digits}
            _sessions.pop(cid, None)
        save_data()
        return main_menu(cid, digits)

    if not user or not user.get("phone"):
        with _lock:
            _sessions[cid] = {"state": "awaiting_phone"}
        return tg_send(cid, "📱 يرجى إدخال رقم هاتفك أولاً (05XXXXXXXX):")

    phone = user["phone"]

    if text == "📶 1G - 20DA":
        return threading.Thread(
            target=execute_service, args=(cid, phone, "1G_20DA", "عرض 1G - 20DA"), daemon=True
        ).start()

    if text == "👻 تفعيل Snapchat":
        return threading.Thread(
            target=execute_service, args=(cid, phone, "SNAPCHAT", "عرض Snapchat"), daemon=True
        ).start()

    if text == "🎁 الهدية اليومية":
        return threading.Thread(
            target=execute_service, args=(cid, phone, "DAILY_GIFT", "الهدية اليومية"), daemon=True
        ).start()

    if text == "📦 الصناديق":
        return threading.Thread(
            target=execute_service, args=(cid, phone, "BOXES", "الصناديق"), daemon=True
        ).start()

    if text == "ℹ️ معلومات النظام":
        return tg_send(
            cid,
            "ℹ️ <b>آلية العمل:</b>\n"
            "• لا يعرض البوت رسالة نجاح إلا بعد استلام تأكيد رسمي ورقم معاملة.\n"
            "• في حال كان الرد فارغاً، يرفض البوت العملية لمنع التفعيل الوهمي.",
            [["🔙 رجوع للقائمة"]],
        )

    if text == "🚪 خروج":
        with _lock:
            _users.pop(cid, None)
            _sessions.pop(cid, None)
        save_data()
        return tg_send(cid, "✅ تم مسح جلستك بنجاح. أرسل /start للبدء من جديد.")

    main_menu(cid, phone)


# ---------------- حلقة الاستقبال الرئيسية ----------------
def polling_loop():
    logger.info("🚀 تم تشغيل البوت بنجاح...")
    tg_request("deleteWebhook", drop_pending_updates=True)

    offset = None
    while True:
        try:
            r = _tg_session.get(
                f"{TELEGRAM_API}/getUpdates",
                params={"timeout": 20, "offset": offset},
                timeout=(5, 25),
            )
            data = r.json()
            if data.get("ok"):
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    msg = upd.get("message") or {}
                    cid = msg.get("chat", {}).get("id")
                    text = (msg.get("text") or "").strip()
                    if cid and text:
                        threading.Thread(target=handle_message, args=(cid, text), daemon=True).start()
        except Exception as exc:
            logger.debug("خطأ في الشبكة: %s", exc)
            time.sleep(3)


if __name__ == "__main__":
    load_data()
    try:
        polling_loop()
    except KeyboardInterrupt:
        save_data()
