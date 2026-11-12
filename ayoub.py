#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ooredoo Telegram Bot — Full OTP & Session Version with Account Management
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

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------- الإعدادات والتهيئة ----------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ooredoo_bot")

TELEGRAM_BOT_TOKEN = "9153869404:AAGI0mkSrZKoF7Ukp6nkKFHyyhZwvtutxHk"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
DATA_FILE = Path(os.getenv("BOT_DATA_FILE", "bot_data.json"))
REQUEST_TIMEOUT = (5, 20)

OOREDOO_BFF = "https://apis.ooredoo.dz/api/ooredoo-bff"
OOREDOO_AUTH = "https://apis.ooredoo.dz/api/auth/realms/myooredoo/protocol/openid-connect/token"
OOREDOO_CLIENT_ID = "myooredoo-app"

_session = requests.Session()
_adapter = HTTPAdapter(
    pool_connections=50,
    pool_maxsize=100,
    max_retries=Retry(total=2, backoff_factor=0.3, status_forcelist=(502, 503, 504)),
)
_session.mount("https://", _adapter)

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


def check_cooldown(cid, seconds=10):
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
    if s.startswith("213") and len(s) == 12:
        s = "0" + s[3:]
    return s[:2] + "x" * (len(s) - 4) + s[-2:] if len(s) >= 8 else s


# ---------------- دوال تليجرام ----------------
def tg_request(method, **kwargs):
    try:
        r = _session.post(
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


# ---------------- المصادقة والتحقق (OTP) ----------------
def oo_send_otp(msisdn):
    try:
        headers = {
            "User-Agent": "Dart/3.11 (dart:io)",
            "Accept-Encoding": "gzip",
            "x-msisdn": msisdn,
            "x-platform-origin": "mobile-android",
            "platform": "android",
            "x-version": "1.5.19",
        }
        r = _session.post(f"{OOREDOO_BFF}/checkpoint/token", headers=headers, data="{}", timeout=8, verify=False)
        if r.status_code in (200, 201):
            nonce = r.headers.get("x-nonce-id")
            chronos = r.headers.get("x-chronos-id")
            if nonce and chronos:
                auth_headers = {
                    "User-Agent": "Dart/3.11 (dart:io)",
                    "x-msisdn": msisdn,
                    "x-nonce-id": nonce,
                    "x-chronos-id": chronos,
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                auth_data = {"client_id": OOREDOO_CLIENT_ID, "grant_type": "password", "username": msisdn}
                r_auth = _session.post(OOREDOO_AUTH, headers=auth_headers, data=auth_data, timeout=8, verify=False)
                if r_auth.status_code in (200, 401, 403):
                    return {"ok": True, "nonce": nonce, "chronos": chronos}
        return {"error": "فشل إرسال الرمز"}
    except Exception as e:
        return {"error": str(e)}


def oo_verify_otp(msisdn, otp, nonce, chronos):
    try:
        headers = {
            "User-Agent": "Dart/3.11 (dart:io)",
            "x-msisdn": msisdn,
            "x-nonce-id": nonce,
            "x-chronos-id": chronos,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"client_id": OOREDOO_CLIENT_ID, "grant_type": "password", "username": msisdn, "otp": otp}
        r = _session.post(OOREDOO_AUTH, headers=headers, data=data, timeout=8, verify=False)
        if r.status_code == 200:
            res = r.json()
            if "access_token" in res:
                return {"access_token": res["access_token"], "refresh_token": res.get("refresh_token", "")}
        return "wrong_otp"
    except:
        return False


# ---------------- تنفيذ الطلبات الفعلي ----------------
def validate_provider_response(response_data, raw_text):
    if not raw_text or not raw_text.strip():
        return False, "استجابة فارغة أو غير صالحة من الخادم (Empty Body)."

    if response_data and isinstance(response_data, dict):
        tx_id = response_data.get("transaction_id") or response_data.get("orderId")
        status = str(response_data.get("status", "")).upper()
        if status in ("CONFIRMED", "SUCCESS", "ACTIVE") or tx_id:
            return True, f"تم التأكيد بنجاح (رقم المعاملة: {tx_id or 'متاح'})"
        
        err_msg = response_data.get("message") or response_data.get("error")
        if err_msg:
            return False, str(err_msg)

    return False, f"رد غير متوقع من السيرفر: {raw_text[:150]}"


def execute_ooredoo_request(endpoint_path, phone, token, payload_data=None):
    url = f"{OOREDOO_BFF}/{endpoint_path}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "x-msisdn": phone,
    }
    try:
        if payload_data is not None:
            r = _session.post(url, headers=headers, json=payload_data, timeout=12, verify=False)
        else:
            r = _session.get(url, headers=headers, timeout=12, verify=False)

        body_text = r.text
        json_data = None
        try:
            json_data = r.json()
        except:
            pass

        if r.status_code in (200, 201):
            return validate_provider_response(json_data, body_text)
        elif r.status_code == 401:
            return False, "انتهت صلاحية جلسة الحساب (رمز التوكن غير صالح). يرجى إعادة إدخال الرقم."
        else:
            return False, f"فشل الطلب (HTTP Status: {r.status_code})"
    except Exception as e:
        return False, f"خطأ في الاتصال بالشبكة: {str(e)}"


def handle_ooredoo_action(operation_code, phone, token):
    if operation_code == "1G_20DA":
        payload = {
            "bundleCode": "1G_20DA",
            "channel": "MOBILE_APP",
            "paymentMethod": "MAIN_BALANCE",
            "msisdn": phone,
            "autoRenewal": False
        }
        return execute_ooredoo_request("cvm/dynamic-bundle-purchase", phone, token, payload)

    elif operation_code == "SNAPCHAT":
        return execute_ooredoo_request("snap-chat/apply", phone, token, {})

    elif operation_code == "DAILY_GIFT":
        return execute_ooredoo_request("gamification/play", phone, token, {})

    elif operation_code == "BOXES":
        return execute_ooredoo_request("gamification/power-snake?status=AVAILABLE", phone, token, None)

    return False, "عملية غير معروفة."


# ---------------- واجهة القوائم ----------------
def main_menu(cid, phone):
    tg_send(
        cid,
        f"📱 <b>الحساب المسجل:</b> <code>{mask_phone(phone)}</code>\nاختر الخدمة المطلوبة من القائمة 👇🏻",
        [
            ["📶 1G - 20DA", "👻 تفعيل Snapchat"],
            ["🎁 الهدية اليومية", "📦 الصناديق"],
            ["⚙️ إدارة الحساب", "🚪 تسجيل خروج"],
        ],
    )


def account_menu(cid, phone):
    tg_send(
        cid,
        f"⚙️ <b>إدارة الحساب المسجل:</b> <code>{mask_phone(phone)}</code>\nاختر الإجراء المناسب:",
        [
            ["🔄 تغيير أو إضافة رقم آخر"],
            ["🗑️ حذف الرقم الحالي من البوت"],
            ["🔙 رجوع للقائمة"],
        ],
    )


def execute_service(cid, user, operation_code, title):
    wait = check_cooldown(cid, seconds=10)
    if wait > 0:
        return tg_send(cid, f"⚠️ يرجى الانتظار <b>{wait} ثانية</b> قبل إرسال طلب جديد.")

    phone = user.get("phone")
    token = user.get("access_token")

    tg_send(cid, f"⏳ جاري إرسال الطلب وتنفيذ <b>{title}</b>...")
    success, message = handle_ooredoo_action(operation_code, phone, token)

    if success:
        tg_send(
            cid,
            f"🎉 <b>نجحت العملية ({title})</b>\n"
            f"📱 <b>الرقم:</b> <code>{mask_phone(phone)}</code>\n"
            f"✅ <b>التفاصيل:</b> {message}",
            [["🔙 رجوع للقائمة"]],
        )
    else:
        tg_send(
            cid,
            f"❌ <b>تعذر إتمام الطلب ({title})</b>\n"
            f"📱 <b>الرقم:</b> <code>{mask_phone(phone)}</code>\n"
            f"🔍 <b>السبب الفعلي:</b> {message}",
            [["🔙 رجوع للقائمة"]],
        )


def handle_message(cid, text):
    with _lock:
        user = dict(_users[cid]) if cid in _users else None
        sess = dict(_sessions.get(cid, {}))

    state = sess.get("state", "")

    if text == "/start":
        with _lock:
            _sessions.pop(cid, None)
        if user and user.get("access_token"):
            return main_menu(cid, user["phone"])
        with _lock:
            _sessions[cid] = {"state": "awaiting_phone"}
        return tg_send(cid, "👋 مرحباً بك في بوت أورييدو الاحترافي 🇩🇿\nأرسل رقم هاتف Ooredoo الخاص بك (05XXXXXXXX) للمتابعة:")

    if state == "awaiting_phone":
        digits = "".join(c for c in text if c.isdigit())
        if not re.match(r"^05\d{8}$", digits):
            return tg_send(cid, "❌ صيغة الرقم غير صحيحة. أرسل رقماً يبدأ بـ 05 (مثال: 0550123456):")
        
        msisdn = "213" + digits[1:]
        tg_send(cid, "⏳ جاري إرسال رمز التحقق (OTP) إلى هاتفك...")
        
        res = oo_send_otp(msisdn)
        if res.get("ok"):
            with _lock:
                _sessions[cid] = {
                    "state": "awaiting_otp",
                    "msisdn": msisdn,
                    "nonce": res.get("nonce"),
                    "chronos": res.get("chronos"),
                }
            return tg_send(cid, "✅ تم إرسال الرمز بنجاح.\nأرسل رمز التحقق (OTP) المكون من 6 أرقام هنا:")
        else:
            return tg_send(cid, "⚠️ فشل إرسال الرمز، تأكد من الرقم أو حاول لاحقاً.")

    if state == "awaiting_otp":
        if not text.isdigit() or len(text) != 6:
            return tg_send(cid, "❌ رمز OTP يجب أن يكون 6 أرقام صحيحة. أعد إرساله:")
        
        msisdn = sess.get("msisdn")
        nonce = sess.get("nonce")
        chronos = sess.get("chronos")

        tg_send(cid, "⏳ جاري التحقق من الرمز وتوليد الجلسة...")
        verify_res = oo_verify_otp(msisdn, text, nonce, chronos)

        if verify_res == "wrong_otp":
            return tg_send(cid, "❌ الرمز خاطئ. تأكد من الرمز وأعد إرساله:")
        if not verify_res:
            return tg_send(cid, "❌ عذراً،فشل الاتصال بخادم أورييدو للتحقق من الرمز.")

        with _lock:
            _users[cid] = {"phone": msisdn, **verify_res}
            _sessions.pop(cid, None)
        save_data()

        tg_send(cid, "🎉 تم تسجيل الدخول وحفظ الجلسة بنجاح!")
        return main_menu(cid, msisdn)

    if not user or not user.get("access_token"):
        with _lock:
            _sessions[cid] = {"state": "awaiting_phone"}
        return tg_send(cid, "📱 يرجى إدخال رقم هاتفك أولاً (05XXXXXXXX):")

    phone = user["phone"]

    # أزرار إدارة الحساب
    if text == "⚙️ إدارة الحساب":
        return account_menu(cid, phone)

    if text == "🔄 تغيير أو إضافة رقم آخر" or text == "🗑️ حذف الرقم الحالي من البوت":
        with _lock:
            _users.pop(cid, None)
            _sessions[cid] = {"state": "awaiting_phone"}
        save_data()
        return tg_send(cid, "🗑️ تم حذف الرقم بنجاح.\n\n📱 أرسل رقم هاتف Ooredoo الجديد (05XXXXXXXX):")

    if text == "📶 1G - 20DA":
        return threading.Thread(
            target=execute_service, args=(cid, user, "1G_20DA", "عرض 1G - 20DA"), daemon=True
        ).start()

    if text == "👻 تفعيل Snapchat":
        return threading.Thread(
            target=execute_service, args=(cid, user, "SNAPCHAT", "عرض Snapchat"), daemon=True
        ).start()

    if text == "🎁 الهدية اليومية":
        return threading.Thread(
            target=execute_service, args=(cid, user, "DAILY_GIFT", "الهدية اليومية"), daemon=True
        ).start()

    if text == "📦 الصناديق":
        return threading.Thread(
            target=execute_service, args=(cid, user, "BOXES", "الصناديق"), daemon=True
        ).start()

    if text == "🚪 تسجيل خروج":
        with _lock:
            _users.pop(cid, None)
            _sessions.pop(cid, None)
        save_data()
        return tg_send(cid, "✅ تم تسجيل الخروج وحذف بياناتك بنجاح. أرسل /start للبدء من جديد.")

    if text == "🔙 رجوع للقائمة":
        return main_menu(cid, phone)

    main_menu(cid, phone)


# ---------------- التشغيل الرئيسي ----------------
def polling_loop():
    logger.info("🚀 تم تشغيل البوت بنجاح...")
    tg_request("deleteWebhook", drop_pending_updates=True)

    offset = None
    while True:
        try:
            r = _session.get(
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
