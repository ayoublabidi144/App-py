#!/usr/init/env python3
# -*- coding: utf-8 -*-
"""
⚡ MATRIX BOT — DAILY GIFT (GAMIFICATION) & SNAPCHAT SUPPORTED
"""

import requests, time, re, json, threading, logging, sys
import uuid, base64, os, urllib3
from urllib.parse import urlencode
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger("matrix_bot")

TELEGRAM_BOT_TOKEN = "9153869404:AAGI0mkSrZKoF7Ukp6nkKFHyyhZwvtutxHk"
TELEGRAM_API  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
ADMIN_ID      = 0
LOG_CHANNEL_ID = "-000000000"

OOREDOO_BFF   = "https://apis.ooredoo.dz/api/ooredoo-bff"
OOREDOO_AUTH  = "https://apis.ooredoo.dz/api/auth/realms/myooredoo/protocol/openid-connect/token"
OOREDOO_CLIENT_ID   = "myooredoo-app"
OOREDOO_X_VERSION   = "1.5.19"
OOREDOO_X_SIG       = "5c7641dbb82cf11066df68afc91541c967640106a95192740b43d51a5ce6777a"
OOREDOO_PLATFORM         = "android"
OOREDOO_PLATFORM_ORIGIN  = "mobile-android"

OOREDOO_INTEGRITY_1 = "JWBTpxXcH7KY9EXYeIRp8NjQMx2dt3vF8ejjoARazyoFzOw6Cu8+wkeV+zSVHSTeI6a12SG/FU+Q/9uBrcN71RlYO4CulD2x375NKwJRAInar8DVUilHBKUfjEsoHd6EwfLCfdYzLNXJu9POfEf6tqKn3PUe0pY6qZxWLhyVAFHw8Qwb52ZqdI2soCH4S3mrz+OZL+YovdGSUKlXKIkxVroAMTAg3jljLF7gvXaEsB/O3uW+tbkBMwSX2uTOwf+rh3sgOF/zPhKCFgRvZmU1o87Fa96Y/+wOcK+UpfXTCBYVrvQ1wG6ryC7vHMSqgUhYJK4tbSoti0zv4av9pwxh9Iv2MgsMENjyKBK/TuFZxEG3xQCKj1LTMgn2xBEeKcbsKrEW3xDRwsccGI3D7GHnbUlhdI4ujDIRQVKHaZSwhTp+32Cr4EB/Qt8p/xRbdgCde9MUlM4AYIGlfyVoHSkOvTu5c0DIIy1EhowtAkbKIJl49wsYKWvpT/nXFWzeXP3R2qzaclCnIb9qihhrarmwz8l8XH2T+f7AK2uSNiuWLG5Fy2mM/YLmuJPZT9Ciag/mpy7JGImKNQAcFbSAInBdKQjUKT+COzZfrXj5rwil9/HDMtuzIovq8hrQGY+roTfVPheTLWmcjkVCOL8VXAHjPb22vOuqrkMioWT9CQ5O8RgW7RKHrObeKQMp8F7tSjOqkxYDFkPVN1G4nkEBrTlPKK9YtPl+j7IuH9fGcDTwhCTTqP8peuBryW0L11tApvAEi7VkJyBxpVxW"
OOREDOO_INTEGRITY_2 = "JWBTpxXcH7KR/kzaHeUUydDWODuU4i3H4fL9gCgKzyYfyN4qLJJE8keV+zSVHSTeI6aEyC2tbSza/NGmkflQ/UgaNZSN9SKxz7tcdQckHY25n6mOaDZ9PPMQmF4sKZqDwebce/c1SNGNn6qvTULW/L348aJvy7Vii6dyPTu3OSPV9AwKwGwQKNHN61HyK3jx/fa8Os5ux9u3Q654YLZrAJ99QGEm/C9nEBPmlHC98RjovLGBnuJOGx6k7fnyrt/Ogy5fNg+tBgi5HEsoXDAwutX7TOWfx4YKHpKW//TvPRQgp69e2Xqa+CvGJJ+a/WlPMPhRCSsfo0OG04mVvlkc8eXiLzV/GPuJCEmcRf9Z6V+xoDyMtU7OZ3XT5BMhI/D/N68LsRn/9dIBH6X7n0WAW3tzeKZK1zENWFKrd7aLlzEdwFzO/1JTQsEDom5TRie0Kd5yic4BGvS1C1BsA2wJhzyiZ2j7RUE9m8tOAkPEIs929FYIfmH8XcCQKHT0TqT0+N+wCiyfNawPlDhZWcObscFZeEmKgvqiUFCoCj6xI1hvyHK0nu7fnZ/sGc6oNT/SrFjubYWjOyoYFL7gMnlYAhyjZhjuAwN1m1/wjwrOx8DbFr2NW8qb3hv+CIzK1zL3LDryKjqNkTxcOp4aJnmSTa73guCEmWc7pnLkLw5O8RgW7RKHrObeeQ0l9lu4HWXwlhdWRxvVMQDimhtTrGASL6sIuaxyhOkrH4HFImP70SaCoK9+euMxnzkPjg9HqPIFj+I0KSMloVxW"

_oo_session = requests.Session()
_tg_session = requests.Session()

_oo_adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100, pool_block=False)
_oo_session.mount("https://", _oo_adapter)
_oo_session.headers.update({"Accept-Encoding": "gzip, deflate", "Connection": "keep-alive"})

_adapter = HTTPAdapter(
    pool_connections=100, pool_maxsize=200,
    max_retries=Retry(total=1, connect=1, read=1, status=1,
                      backoff_factor=0.2, status_forcelist=(502,503,504)),
    pool_block=False)
_tg_session.mount("https://", _adapter)
_tg_session.mount("http://",  _adapter)

DATA_FILE = "bot_data.json"
_lock, _save_lock = threading.Lock(), threading.Lock()
_save_pending = {"flag": False}
_users, _sessions, _devices = {}, {}, {}
_bot_stats = {"users": 0, "activations": 0}
_maintenance = False
_otp_cooldown, _otp_cooldown_lock = {}, threading.Lock()

def _check_otp_cooldown(cid):
    now = time.time()
    with _otp_cooldown_lock:
        last = _otp_cooldown.get(cid, 0)
        if now - last < 60:
            return int(60 - (now - last))
        _otp_cooldown[cid] = now
    return 0

def _do_save():
    with _save_lock:
        try:
            data = {
                "users": {str(k): v for k, v in _users.items()},
                "devices": {str(k): v for k, v in _devices.items()},
                "stats": _bot_stats,
                "maintenance": _maintenance,
            }
            tmp = DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            os.replace(tmp, DATA_FILE)
            _save_pending["flag"] = False
        except Exception as e:
            logger.warning(f"save: {e}")

def _save_async():
    if _save_pending["flag"]: return
    _save_pending["flag"] = True
    def _d():
        time.sleep(2); _do_save()
    threading.Thread(target=_d, daemon=True).start()

def _load_from_disk():
    global _users, _devices, _bot_stats, _maintenance
    if not os.path.exists(DATA_FILE): return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _users = {int(k): v for k, v in data.get("users", {}).items()}
        _devices = {int(k): v for k, v in data.get("devices", {}).items()}
        _bot_stats = data.get("stats", {"users": 0, "activations": 0})
        _maintenance = data.get("maintenance", False)
        logger.info(f"✅ Loaded {len(_users)} users")
    except Exception as e:
        logger.warning(f"load: {e}")

def oo_get_user(cid):
    with _lock: return dict(_users.get(cid)) if _users.get(cid) else None

def oo_save_user(cid, data):
    with _lock:
        if cid not in _users:
            _users[cid] = {}; _bot_stats["users"] += 1
        changed = False
        for k, v in data.items():
            if v is not None and _users[cid].get(k) != v:
                _users[cid][k] = v; changed = True
    if changed: _save_async()

def oo_delete_user(cid):
    with _lock: _users.pop(cid, None)
    _save_async()

def oo_get_session(cid):
    with _lock: return dict(_sessions.get(cid)) if _sessions.get(cid) else {}

def oo_set_session(cid, data):
    with _lock:
        if cid not in _sessions: _sessions[cid] = {}
        _sessions[cid].update({k: v for k, v in data.items() if v is not None})

def oo_clear_session(cid):
    with _lock: _sessions.pop(cid, None)

def oo_get_device(cid):
    iid = oo_new_iid()
    return {"instance_id": iid, "plat_sig": oo_new_psig(iid)}

def oo_now_ms():  return str(int(time.time() * 1000))
def oo_new_iid():
    u = uuid.uuid4().hex
    return f"{u[:8]}-{u[8:12]}-11{u[12:16]}-{u[16:20]}-{u[20:32]}{oo_now_ms()}"
def oo_new_psig(iid):
    p = json.dumps({"platform": "android", "is-physical-device": True, "device-id": iid}, separators=(",", ":"))
    return base64.b64encode(p.encode()).decode()
def oo_new_corr(): return uuid.uuid4().hex + oo_now_ms()
def oo_new_fp():   return uuid.uuid4().hex + uuid.uuid4().hex[:32]
def oo_decode_jwt(token):
    if not token: return {}
    try:
        p = token.split(".")[1]; p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p))
    except: return {}
def oo_extract_did(token): return oo_decode_jwt(token).get("device-id")

def mask_phone(m):
    if not m: return "—"
    s = str(m).strip()
    if s.startswith("213") and len(s) == 12: s = "0" + s[3:]
    return s[:2] + "x" * (len(s) - 4) + s[-2:] if len(s) >= 8 else s

def oo_http(method, url, headers, body="", timeout=6):
    try:
        if method == "GET":
            r = _oo_session.get(url, headers=headers, timeout=timeout, verify=False)
        elif method == "POST":
            r = _oo_session.post(url, headers=headers, data=body, timeout=timeout, verify=False)
        else:
            return None
        txt = r.text
        if "Request Rejected" in txt or "support id" in txt.lower():
            return {"ip_blocked": True, "code": r.status_code}
        try: j = r.json()
        except: j = None
        return {"code": r.status_code, "body": txt,
                "headers": {k.lower(): v for k, v in r.headers.items()}, "json": j}
    except Exception as e:
        logger.debug(f"http err: {e}")
        return None

def oo_base_h(msisdn, fp, corr, ts, iid, psig):
    return {
        "User-Agent": "Dart/3.11 (dart:io)", "Accept-Encoding": "gzip",
        "x-msisdn": msisdn, "x-device-fingerprint": fp,
        "x-platform-origin": OOREDOO_PLATFORM_ORIGIN, "x-correlation-id": corr,
        "platform": OOREDOO_PLATFORM, "x-version": OOREDOO_X_VERSION,
        "x-signature": OOREDOO_X_SIG, "x-platform-data-signature": psig,
        "x-timestamp": ts, "x-instance-id": iid,
    }

def oo_authed_h(msisdn, token, tokh):
    ts   = tokh.get("tok_timestamp")   or oo_now_ms()
    iid  = tokh.get("tok_instance_id") or oo_new_iid()
    psig = tokh.get("tok_plat_sig")    or oo_new_psig(iid)
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "x-msisdn": msisdn, "x-device-fingerprint": oo_new_fp(),
        "x-platform-origin": "web", "authorization": f"Bearer {token}",
        "x-correlation-id": oo_new_corr(), "platform": "web",
        "x-version": OOREDOO_X_VERSION, "x-signature": OOREDOO_X_SIG,
        "x-platform-data-signature": psig, "x-timestamp": ts, "x-instance-id": iid,
        "origin": "https://my.ooredoo.dz", "referer": "https://my.ooredoo.dz/",
    }

def oo_send_otp(msisdn, device=None):
    last_error = "unknown"
    for attempt in range(2):
        try:
            iid = oo_new_iid(); psig = oo_new_psig(iid); ts = oo_now_ms()
            h3 = oo_base_h(msisdn, oo_new_fp(), oo_new_corr(), ts, iid, psig)
            h3["content-type"] = "application/json; charset=utf-8"
            h3["x-native-integrity-token"] = OOREDOO_INTEGRITY_1
            h3["x-path"]   = "/api/auth/realms/myooredoo/protocol/openid-connect/token"
            h3["x-method"] = "POST"
            r3 = oo_http("POST", f"{OOREDOO_BFF}/checkpoint/token", h3, "{}", timeout=8)

            if not r3 or r3.get("ip_blocked"):
                last_error = "ip_blocked"; time.sleep(3); continue
            nonce   = r3["headers"].get("x-nonce-id")
            chronos = r3["headers"].get("x-chronos-id")
            if not nonce or not chronos:
                last_error = "checkpoint_failed"; time.sleep(2); continue

            h4 = {
                "User-Agent": "Dart/3.11 (dart:io)", "Accept-Encoding": "gzip",
                "x-msisdn": msisdn, "x-device-fingerprint": oo_new_fp(),
                "x-nonce-id": nonce, "x-platform-origin": OOREDOO_PLATFORM_ORIGIN,
                "platform": OOREDOO_PLATFORM, "x-version": OOREDOO_X_VERSION,
                "x-signature": OOREDOO_X_SIG, "x-chronos-id": chronos,
                "x-timestamp": ts, "x-platform-info": psig, "x-force-update": "true",
                "x-instance-id": iid, "Content-Type": "application/x-www-form-urlencoded",
            }
            b4 = urlencode({"client_id": OOREDOO_CLIENT_ID, "grant_type": "password", "username": msisdn})
            r4 = oo_http("POST", OOREDOO_AUTH, h4, b4, timeout=10)
            if not r4:
                last_error = "network"; time.sleep(3); continue
            c4 = r4.get("code")
            if c4 in (401, 403, 200): return {"ok": True}
            if c4 == 429:
                last_error = "rate_limit"; time.sleep(5); continue
            last_error = f"http_{c4}"; time.sleep(2)
        except Exception as e:
            last_error = str(e); time.sleep(2)
    return {"error": last_error}

def oo_verify_otp(msisdn, otp, device):
    iid, psig, ts = device["instance_id"], device["plat_sig"], oo_now_ms()
    h6 = oo_base_h(msisdn, oo_new_fp(), oo_new_corr(), ts, iid, psig)
    h6["content-type"] = "application/json; charset=utf-8"
    h6["x-native-integrity-token"] = OOREDOO_INTEGRITY_2
    h6["x-path"]   = "/api/auth/realms/myooredoo/protocol/openid-connect/token"
    h6["x-method"] = "POST"
    r6 = oo_http("POST", f"{OOREDOO_BFF}/checkpoint/token", h6, "{}", timeout=6)
    if not r6 or r6.get("ip_blocked"): return False
    n2 = r6["headers"].get("x-nonce-id"); c2 = r6["headers"].get("x-chronos-id")
    if not n2 or not c2: return False

    fp7 = oo_new_fp()
    h7 = {
        "User-Agent": "Dart/3.11 (dart:io)", "Accept-Encoding": "gzip",
        "x-msisdn": msisdn, "x-device-fingerprint": fp7, "x-nonce-id": n2,
        "x-platform-origin": OOREDOO_PLATFORM_ORIGIN, "platform": OOREDOO_PLATFORM,
        "x-version": OOREDOO_X_VERSION, "x-signature": OOREDOO_X_SIG,
        "x-chronos-id": c2, "x-timestamp": ts, "x-platform-info": psig,
        "x-force-update": "true", "x-instance-id": iid,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    b7 = urlencode({"client_id": OOREDOO_CLIENT_ID, "grant_type": "password",
                    "username": msisdn, "otp": otp})
    r7 = oo_http("POST", OOREDOO_AUTH, h7, b7, timeout=8)
    c7 = r7.get("code") if r7 else None
    if c7 in (401, 403): return "wrong_otp"
    if c7 == 200 and r7.get("json") and "access_token" in r7["json"]:
        j = r7["json"]
        return {
            "access_token": j["access_token"], "refresh_token": j.get("refresh_token", ""),
            "tok_fingerprint": fp7, "tok_timestamp": ts,
            "tok_instance_id": oo_extract_did(j["access_token"]) or iid,
            "tok_plat_sig": psig, "tok_correlation": oo_new_corr(),
        }
    return False

def oo_refresh_token(user, device):
    rt = user.get("refresh_token", "")
    if not rt: return "expired"
    iid  = user.get("tok_instance_id") or device["instance_id"]
    psig = user.get("tok_plat_sig")    or device["plat_sig"]
    ts   = oo_now_ms()
    payload = {"grant_type": "refresh_token", "client_id": OOREDOO_CLIENT_ID, "refresh_token": rt}
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded",
               "Origin": "https://my.ooredoo.dz", "Referer": "https://my.ooredoo.dz/"}
    try:
        r = _oo_session.post(OOREDOO_AUTH, data=payload, headers=headers, timeout=8, verify=False)
        if r.status_code == 200:
            res = r.json()
            if res.get("access_token"):
                return {
                    "access_token": res["access_token"], "refresh_token": res.get("refresh_token", rt),
                    "tok_fingerprint": oo_new_fp(), "tok_timestamp": ts,
                    "tok_instance_id": oo_extract_did(res["access_token"]) or iid,
                    "tok_plat_sig": psig, "tok_correlation": oo_new_corr(),
                }
        return "expired"
    except: return False

def oo_check_session(user, cid):
    if not user or not user.get("access_token"): return False
    dev = oo_get_device(cid)
    h = oo_authed_h(user["msisdn"], user["access_token"], {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    r = oo_http("GET", f"{OOREDOO_BFF}/users/validateUser?msisdn={user['msisdn']}", h, timeout=5)
    if r and r["code"] == 200: return True
    if r and r["code"] == 401:
        nt = oo_refresh_token(user, dev)
        if isinstance(nt, dict):
            user.update(nt); oo_save_user(cid, user); return True
    return False

def oo_call_refresh(cid, func, msisdn, user, *a):
    res = func(msisdn, user, *a)
    if isinstance(res, dict) and (res.get("_need_refresh") or res.get("auth_error")):
        dev = oo_get_device(cid)
        nt  = oo_refresh_token(user, dev)
        if nt == "expired": return {"error": "expired"}
        if not nt:          return {"error": "refresh_failed"}
        user.update(nt); oo_save_user(cid, user)
        res = func(msisdn, user, *a)
    return res

def oo_buy_cvm(msisdn, user, bundle_code):
    h = oo_authed_h(msisdn, user.get("access_token"), {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    h["content-type"] = "application/json; charset=utf-8"
    
    payload = {
        "bundleCode": bundle_code,
        "channel": "MOBILE_APP",
        "paymentMethod": "MAIN_BALANCE",
        "msisdn": msisdn,
        "autoRenewal": False
    }
    
    r = oo_http("POST", f"{OOREDOO_BFF}/cvm/dynamic-bundle-purchase", h, json.dumps(payload), timeout=10)
    if not r: return {"error": "فشل الاتصال بالخادم"}
    
    code = r["code"]
    body_txt = r.get("body") or ""
    body_lower = body_txt.lower()
    j_res = r.get("json")

    print(f"DEBUG CVM RESP -> Code: {code}, Body: {body_txt}")

    if code not in (200, 201):
        return {"error": "💰 الرصيد غير كافي لتفعيل العرض"}

    if isinstance(j_res, dict):
        if j_res.get("success") is False or str(j_res.get("status", "")).upper() in ("ERROR", "FAIL", "FAILED", "REJECTED"):
            return {"error": "💰 الرصيد غير كافي لتفعيل العرض"}
        if j_res.get("success") is True or str(j_res.get("status", "")).upper() in ("SUCCESS", "OK", "ACTIVE"):
            return {"success": True}

    reject_keywords = ["insufficient", "balance", "solde", "رصيد", "not enough", "error", "fail", "failed", "مرفوض", "غير كافي", "expired", "invalid", "unavailable", "denied", "amount"]
    if any(w in body_lower for w in reject_keywords):
        return {"error": "💰 الرصيد غير كافي لتفعيل العرض"}

    if not body_txt.strip() or body_txt.strip() in ("{}", "[]"):
        return {"error": "💰 الرصيد غير كافي لتفعيل هذا العرض"}

    if "success" not in body_lower and "bundle" not in body_lower and "transaction" not in body_lower:
        return {"error": "💰 الرصيد غير كافي لتفعيل العرض"}

    return {"success": True}

def oo_apply_snapchat(msisdn, user):
    h = oo_authed_h(msisdn, user.get("access_token"), {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    h["content-type"] = "application/json; charset=utf-8"
    
    r = oo_http("POST", f"{OOREDOO_BFF}/snap-chat/apply", h, "{}", timeout=10)
    if not r: return {"error": "فشل الاتصال بالخادم"}
    
    code = r["code"]
    body_txt = r.get("body") or ""
    j_res = r.get("json")
    
    print(f"DEBUG SNAP RESP -> Code: {code}, Body: {body_txt}")
    
    if code in (200, 201):
        if isinstance(j_res, dict):
            if j_res.get("success") is False or j_res.get("status") in ("ERROR", "FAIL"):
                return {"error": f"⚠️ {j_res.get('message', 'فشل تفعيل العرض')}"}
            if j_res.get("success") is True or j_res.get("status") in ("SUCCESS", "OK"):
                return {"success": True}
        
        if not body_txt.strip() or body_txt.strip() in ("{}", "[]"):
            return {"error": "❌ رفض الخادم تفعيل العرض (غير متاح لشريحتك)"}
            
        return {"success": True}
        
    return {"error": f"💰 فشل الطلب (كود: {code})"}

def oo_claim_daily_gift(msisdn, user):
    dev = oo_get_device(None)
    iid, psig, ts = dev["instance_id"], dev["plat_sig"], oo_now_ms()
    
    # 1. طلب الـ Checkpoint للحصول على Nonce و Chronos خاص بالهدية اليومية
    h3 = oo_base_h(msisdn, oo_new_fp(), oo_new_corr(), ts, iid, psig)
    h3["content-type"] = "application/json; charset=utf-8"
    h3["x-native-integrity-token"] = OOREDOO_INTEGRITY_1
    h3["x-path"] = "/api/ooredoo-bff/gamification/play"
    h3["x-method"] = "GET"
    
    r3 = oo_http("POST", f"{OOREDOO_BFF}/checkpoint/token", h3, "{}", timeout=8)
    if not r3 or r3.get("ip_blocked"):
        return {"error": "فشل الاتصال بنقطة التحقق (IP Blocked)"}
        
    nonce = r3["headers"].get("x-nonce-id")
    chronos = r3["headers"].get("x-chronos-id")
    if not nonce or not chronos:
        return {"error": "فشل استخراج رموز التحقق للهدية اليومية"}
        
    # 2. الطلب الفعلي للحصول على الهدية
    token = user.get("access_token", "")
    h_play = {
        "User-Agent": "Dart/3.11 (dart:io)",
        "Accept-Encoding": "gzip",
        "x-msisdn": msisdn,
        "x-device-fingerprint": oo_new_fp(),
        "x-nonce-id":
