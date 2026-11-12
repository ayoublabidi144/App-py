#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ooredoo Telegram Bot — safe, honest starter version.

IMPORTANT:
- This bot does NOT pretend to activate bundles.
- The uploaded source used undocumented Ooredoo endpoints and fabricated
  device/integrity headers. Those mechanisms are intentionally not reproduced.
- Connect only an official Ooredoo API/partner interface whose documentation
  and credentials you are authorized to use.
"""

import json
import logging
import os
import time
from pathlib import Path
from threading import Lock

import requests

# ---------------- Configuration ----------------

BOT_TOKEN = "9153869404:AAGI0mkSrZKoF7Ukp6nkKFHyyhZwvtutxHk"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""
DATA_FILE = Path(os.getenv("BOT_DATA_FILE", "bot_data.json"))
REQUEST_TIMEOUT = (5, 20)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ooredoo_bot")

http = requests.Session()
http.headers.update({"User-Agent": "OoredooTelegramBot/1.0"})
data_lock = Lock()
users = {}


# ---------------- Persistent data ----------------

def load_data():
    global users
    if not DATA_FILE.exists():
        users = {}
        return
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        users = raw.get("users", {}) if isinstance(raw, dict) else {}
        if not isinstance(users, dict):
            users = {}
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Could not load data file: %s", exc)
        users = {}


def save_data():
    with data_lock:
        temp = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
        try:
            temp.write_text(
                json.dumps({"users": users}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temp, DATA_FILE)
        except OSError:
            log.exception("Could not save data")
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass


# ---------------- Telegram API ----------------

def tg_call(method, payload=None):
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    try:
        response = http.post(
            f"{TELEGRAM_API}/{method}",
            json=payload or {},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            log.error("Telegram API error in %s: %s", method, result)
            return None
        return result.get("result")
    except (requests.RequestException, ValueError):
        log.exception("Telegram request failed: %s", method)
        return None


def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if keyboard:
        payload["reply_markup"] = {
            "keyboard": [[{"text": item} for item in row] for row in keyboard],
            "resize_keyboard": True,
        }
    return tg_call("sendMessage", payload)


def main_menu(chat_id):
    send_message(
        chat_id,
        "مرحباً بك في بوت خدمات Ooredoo 🇩🇿\n\n"
        "اختر الخدمة. لن يعرض البوت نجاح أي عملية إلا بعد تأكيدها "
        "من واجهة Ooredoo الرسمية.",
        [
            ["📶 حالة خدمة 1G", "👻 حالة Snapchat"],
            ["🎁 الهدية اليومية", "📦 الصناديق"],
            ["ℹ️ معلومات", "🚪 خروج"],
        ],
    )


# ---------------- Official API integration boundary ----------------

def official_ooredoo_operation(operation, phone=None):
    """
    Implement this function only with Ooredoo's documented, authorized API.

    Expected return shape:
        {"success": True, "message": "Confirmed result from provider"}
    or:
        {"success": False, "message": "Provider's actual error"}

    Do not infer success from HTTP 200/201 alone. Validate the documented
    response fields and, where supported, query the resulting subscription
    or transaction status before reporting success.
    """
    return {
        "success": False,
        "message": (
            "هذه الخدمة غير مربوطة حالياً بواجهة Ooredoo رسمية موثقة. "
            "لم يتم إرسال طلب تفعيل، ولم يتم خصم أي رصيد بواسطة هذا البوت."
        ),
    }


def run_service(chat_id, operation):
    send_message(chat_id, "⏳ جارٍ التحقق من توفر الخدمة...")
    result = official_ooredoo_operation(operation)
    if result.get("success") is True:
        send_message(chat_id, "✅ " + str(result.get("message", "تم التأكيد.")))
    else:
        send_message(chat_id, "⚠️ " + str(result.get("message", "تعذر تأكيد العملية.")))


# ---------------- Message handling ----------------

def handle_message(message):
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()
    if not chat_id or not text:
        return

    if text in ("/start", "/menu", "🔙 القائمة"):
        main_menu(chat_id)
        return

    if text == "ℹ️ معلومات":
        send_message(
            chat_id,
            "هذا إصدار آمن من البوت.\n"
            "لا يجمع رمز OTP أو كلمة مرور حسابك، ولا يحاكي تطبيق الهاتف "
            "ولا يتجاوز أنظمة الحماية.\n\n"
            "يلزم توثيق رسمي لواجهة API قبل تفعيل الخدمات فعلياً.",
            [["🔙 القائمة"]],
        )
        return

    if text == "📶 حالة خدمة 1G":
        run_service(chat_id, "bundle_1g_20da")
        return

    if text == "👻 حالة Snapchat":
        run_service(chat_id, "snapchat")
        return

    if text == "🎁 الهدية اليومية":
        run_service(chat_id, "daily_gift")
        return

    if text == "📦 الصناديق":
        run_service(chat_id, "power_snake_boxes")
        return

    if text == "🚪 خروج":
        with data_lock:
            users.pop(str(chat_id), None)
        save_data()
        send_message(chat_id, "تم مسح بيانات المستخدم المحلية من هذا البوت.")
        return

    send_message(chat_id, "لم أفهم طلبك. أرسل /start لعرض القائمة.")


def poll_updates():
    offset = None
    log.info("Bot started")
    while True:
        try:
            params = {"timeout": 25}
            if offset is not None:
                params["offset"] = offset
            response = http.get(
                f"{TELEGRAM_API}/getUpdates",
                params=params,
                timeout=(5, 35),
            )
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok"):
                log.warning("getUpdates returned an unsuccessful response")
                time.sleep(3)
                continue

            for update in payload.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message")
                if message:
                    handle_message(message)

        except requests.RequestException as exc:
            log.warning("Telegram polling network error: %s", exc)
            time.sleep(3)
        except Exception:
            log.exception("Unexpected polling error")
            time.sleep(2)


def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN environment variable before starting."
        )
    load_data()
    poll_updates()


if __name__ == "__main__":
    main()
