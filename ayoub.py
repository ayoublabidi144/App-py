#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ OOREDOO TELEGRAM BOT — FULL SESSION & OTP VERSION
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
logger = logging.getLogger("ooredoo_bot")

# توكن البوت الذي أرسلته
TELEGRAM_BOT_TOKEN = "9153869404:AAGI0mkSrZKoF7Ukp6nkKFHyyhZwvtutxHk"
TELEGRAM_API  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

OOREDOO_BFF   = "https://apis.ooredoo.dz/api/ooredoo-bff"
OOREDOO_AUTH  = "https://apis.ooredoo.dz/api/auth/realms/myooredoo/protocol/openid-connect/token"
OOREDOO_CLIENT_ID   = "myooredoo-app"
OOREDOO_X_VERSION   = "1.5.19"
OOREDOO_X_SIG       = "5c7641dbb82cf11066df68afc91541c967640106a95192740b43d51a5ce6777a"
OOREDOO_PLATFORM         = "android"
OOREDOO_PLATFORM_ORIGIN  = "mobile-android"

OOREDOO_INTEGRITY_1 = "JWBTpxXcH7KY9EXYeIRp8NjQMx2dt3vF8ejjoARazyoFzOw6Cu8+wkeV+zSVHSTeI6a12SG/FU+Q/9uBrcN71RlYO4CulD2x375NKwJRAInar8DVUilHBKUfjEsoHd6EwfLCfdYzLNXJu9POfEf6tqKn3PUe0pY6qZxWLhyVAFHw8Qwb52ZqdI2soCH4S3mrz+OZL+YovdGSUKlXKIkxVroAMTAg3jljLF7gvXaEsB/O3uW+tbkBMwSX2uTOwf+rh3sgOF/zPhKCFgRvZmU1o87Fa96Y/+wOcK+UpfXTCBYVrvQ1wG6ryC7vHMSqgUhYJK4tbSoti0zv4av9pwxh9Iv2MgsMENjyKBK/TuFZxEG3xQCKj1LTMgn2xBEeKcbsKrEW3xDRwsccGI3D7GHnbUlhdI4ujDIRQVKHaZSwhTp+32Cr4EB/Qt8p/xRbdgCde9MUlM4AYIGlfyVoHSkOvTu5c0DIIy1EhowtAkbKIJl49wsYKWvpT/nXFWzeXP3R2qzaclCnIb9qihhrarmwz8l8XH2T+f7AK2uSNiuWLG5Fy2mM/YLmuJPZT9Ciag/mpy7JGImKNQAcFbSAInBdKQjUKT+COzZfrXj5rwil9/HDMtuzIovq8hrQGY+roTfVPheTLWmcjkVCOL8VXAHjPb22vOuqrkMioWT9CQ5O8RgW7RKHrObeKQMp8F7tSjOqkxYDFkPVN1G4nkEBrTlPKK9YtPl+j7IuH9fGcDTwhCTTqP8peuBryW0L11tApvAEi7VkJyBxpVxW"
OOREDOO_INTEGRITY_2 = "JWBTpxXcH7KR/kzaHeUUydDWODuU4i3H4fL9gCgKzyYfyN4qLJJE8keV+zSVHSTeI6aEyC2tbSza/NGmkflQ/UgaNZSN9SKxz7tcdQckHY25n6mOaDZ9PPMQmF4sKZqDwebce/c1SNGNn6qvTULW/L348aJvy7Vii6dyPTu3OSPV9AwKwGwQKNHN61HyK3jx/fa8Os5ux9u3Q654YLZrAJ99QGEm/C9nEBPmlHC98RjovLGBnuJOGx6k7fnyrt/Ogy5fNg+tBgi5HEsoXDAwutX7TOWfx4YKHpKW//TvPRQgp69e2Xqa+CvGJJ+a/WlPMPhRCSsfo0OG04mVvlkc8eXiLzV/GPuJCEmcRf9Z6V+xoDyMtU7OZ3XT5BMhI/D/N68LsRn/9dIBH6X7n0WAW3tzeKZK1zENWFKrd7aLlzEdwFzO/1JTQsEDom5TRie0Kd5yic4BGvS1C1BsA2wJhzyiZ2j7RUE9m8tOAkPEIs929FYIfmH8XcCQKHT0TqT0+N+wCiyfNawPlDhZWcObscFZeEmKgvqiUFCoCj6xI1hvyHK0nu7fnZ/sGc6oNT/SrFjubYWjOyoYFL7gMnlYAhyjZhjuAwN1m1/wjwrOx8DbFr2NW8qb3hv+CIzK1zL3LDryKjqNkTxcOp4aJnmSTa73guCEmWc7pnLkLw5O8RgW7RKHrObeKQMp8F7tSjOqkxYDFkPVN1G4nkEBrTlPKK9YtPl+j7IuH9fGcDTwhCTTqP8peuBryW0L11tApvAEi7VkJyBxpVxW"

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
    
    code = r.get("code")
    body_txt = (r.get("body") or "").strip()
    j_res = r.get("json")

    debug_info = f"<b>Code:</b> <code>{code}</code>\n"
    if j_res:
        debug_info += f"<b>JSON:</b>\n<code>{json.dumps(j_res, indent=2, ensure_ascii=False)[:350]}</code>"
    else:
        debug_info += f"<b>Body:</b>\n<code>{body_txt[:300] if body_txt else 'Empty Body'}</code>"

    if code in (200, 201):
        return {"success": True, "debug": debug_info}
    else:
        return {"error": f"فشل التفعيل (HTTP Status: {code})\n\n{debug_info}"}

def oo_apply_snapchat(msisdn, user):
    h = oo_authed_h(msisdn, user.get("access_token"), {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    h["content-type"] = "application/json; charset=utf-8"
    
    r = oo_http("POST", f"{OOREDOO_BFF}/snap-chat/apply", h, "{}", timeout=10)
    if not r: return {"error": "فشل الاتصال بالخادم"}
    
    code = r["code"]
    body_txt = (r.get("body") or "").strip()
    j_res = r.get("json")
    
    debug_info = f"<b>Code:</b> <code>{code}</code>\n"
    if j_res:
        debug_info += f"<b>JSON:</b>\n<code>{json.dumps(j_res, indent=2, ensure_ascii=False)[:350]}</code>"
    else:
        debug_info += f"<b>Body:</b>\n<code>{body_txt[:300] if body_txt else 'Empty Body'}</code>"

    if code in (200, 201):
        return {"success": True, "debug": debug_info}
        
    return {"error": f"💰 فشل الطلب (كود: {code})\n\n{debug_info}"}

def oo_claim_daily_gift(msisdn, user):
    dev = oo_get_device(None)
    iid, psig, ts = dev["instance_id"], dev["plat_sig"], oo_now_ms()
    
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
        
    token = user.get("access_token", "")
    h_play = {
        "User-Agent": "Dart/3.11 (dart:io)", "Accept-Encoding": "gzip",
        "x-msisdn": msisdn, "x-device-fingerprint": oo_new_fp(),
        "x-nonce-id": nonce, "x-chronos-id": chronos,
        "x-platform-origin": OOREDOO_PLATFORM_ORIGIN, "platform": OOREDOO_PLATFORM,
        "x-version": OOREDOO_X_VERSION, "x-signature": OOREDOO_X_SIG,
        "x-platform-data-signature": psig, "x-timestamp": ts, "x-instance-id": iid,
        "authorization": f"Bearer {token}", "x-correlation-id": oo_new_corr(),
    }
    
    r_play = oo_http("GET", f"{OOREDOO_BFF}/gamification/play", h_play, timeout=8)
    if not r_play:
        return {"error": "فشل الاتصال بخادم الهدية اليومية"}
        
    code = r_play["code"]
    body_txt = r_play.get("body") or ""
    body_lower = body_txt.lower()
    
    if code in (200, 201):
        if "already" in body_lower or "deja" in body_lower or "played" in body_lower:
            return {"error": "⚠️ لقد استفدت من الهدية اليومية مسبقاً اليوم."}
        return {"success": True}
        
    return {"error": f"💰 فشل استلام الهدية (كود: {code})"}

def oo_check_power_snake_boxes(msisdn, user):
    h = oo_authed_h(msisdn, user.get("access_token"), {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    r = oo_http("GET", f"{OOREDOO_BFF}/gamification/power-snake?status=AVAILABLE", h, timeout=10)
    if not r or r["code"] not in (200, 201):
        return {"error": "فشل التحقق من الصناديق المتاحة"}
    return {"success": True, "json": r.get("json")}

def oo_redeem_power_snake_box(msisdn, user, box_id):
    h = oo_authed_h(msisdn, user.get("access_token"), {
        "tok_timestamp": user.get("tok_timestamp"),
        "tok_instance_id": user.get("tok_instance_id"),
        "tok_plat_sig": user.get("tok_plat_sig")})
    h["content-type"] = "application/json; charset=utf-8"
    r = oo_http("POST", f"{OOREDOO_BFF}/gamification/power-snake/{box_id}/redeem", h, "{}", timeout=10)
    if not r or r["code"] not in (200, 201):
        return {"error": "فشل فتح الصندوق أو تم فتحه مسبقاً"}
    return {"success": True, "json": r.get("json")}

def tg_request(method, **kwargs):
    try:
        r = _tg_session.post(f"{TELEGRAM_API}/{method}", json=kwargs, timeout=5)
        return r.json()
    except: return None

def tg_send(cid, text, keyboard=None):
    payload = {"chat_id": cid, "text": text, "parse_mode": "HTML"}
    if keyboard: payload["reply_markup"] = {"keyboard": keyboard, "resize_keyboard": True}
    return tg_request("sendMessage", **payload)

def tg_buttons(cid, text, rows):
    return tg_send(cid, text, [[{"text": b} for b in row] for row in rows])

def oo_menu(cid):
    tg_buttons(cid, "اختر من القائمة الرئيسية 👇🏻", [
        ["📶 1G - 20DA", "🎁 عرض 2G مجاناً"],
        ["👻 تفعيل Snapchat", "🎁 الهدية اليومية"],
        ["🎁 التحقق من الصناديق", "📦 فتح الصندوق"],
        ["🚪 خروج"]
    ])

def oo_offers_menu(cid):
    tg_buttons(cid, "🛒 العروض المتوفرة والتفعيل:", [
        ["📶 1G - 20DA", "🎁 عرض 2G مجاناً"],
        ["👻 تفعيل Snapchat", "🎁 الهدية اليومية"],
        ["🎁 التحقق من الصناديق", "📦 فتح الصندوق"],
        ["🔙 رجوع للقائمة"]
    ])

def oo_do_activation(cid, user, bundle_code, name_ar):
    m = user.get("msisdn", "")
    tg_send(cid, f"⏳ جاري تفعيل {name_ar}...")
    res = oo_buy_cvm(m, user, bundle_code)
    if res.get("success"):
        dbg = res.get("debug", "")
        tg_buttons(cid, f"🎉 <b>نتيجة الطلب ({name_ar}):</b>\n📱 <b>الرقم:</b> <code>{mask_phone(m)}</code>\n\n🔍 <b>تفاصيل الاستجابة:</b>\n{dbg}", [["🔙 رجوع للقائمة"]])
    else:
        tg_buttons(cid, f"❌ <b>فشل التفعيل:</b>\n{res.get('error')}", [["🔙 رجوع للقائمة"]])

def oo_do_snapchat(cid, user):
    m = user.get("msisdn", "")
    tg_send(cid, f"⏳ جاري تفعيل عرض Snapchat المجاني...")
    res = oo_apply_snapchat(m, user)
    if res.get("success"):
        dbg = res.get("debug", "")
        tg_buttons(cid, f"🎉 <b>تم تفعيل Snapchat بنجاح 🥳</b>\n📱 <b>الرقم:</b> <code>{mask_phone(m)}</code>\n\n🔍 <b>تفاصيل الاستجابة:</b>\n{dbg}", [["🔙 رجوع للقائمة"]])
    else:
        tg_buttons(cid, f"❌ <b>فشل تفعيل Snapchat:</b>\n{res.get('error')}", [["🔙 رجوع للقائمة"]])

def oo_do_daily_gift(cid, user):
    m = user.get("msisdn", "")
    tg_send(cid, f"⏳ جاري جلب الهدية اليومية...")
    res = oo_call_refresh(cid, oo_claim_daily_gift, m, user)
    if isinstance(res, dict) and res.get("success"):
        tg_buttons(cid, f"🎉 <b>مبروك! تم استلام الهدية اليومية بنجاح 🎁</b>\n📱 <b>الرقم:</b> <code>{mask_phone(m)}</code>", [["🔙 رجوع للقائمة"]])
    else:
        err = res.get('error') if isinstance(res, dict) else "فشل العملية"
        tg_buttons(cid, f"❌ <b>فشل استلام الهدية:</b>\n{err}", [["🔙 رجوع للقائمة"]])

def oo_do_check_boxes(cid, user):
    m = user.get("msisdn", "")
    tg_send(cid, "⏳ جاري التحقق من الصناديق المتاحة...")
    res = oo_call_refresh(cid, oo_check_power_snake_boxes, m, user)
    if isinstance(res, dict) and res.get("success"):
        j = res.get("json")
        tg_buttons(cid, f"🎁 <b>نتيجة التحقق من الصناديق:</b>\n<code>{json.dumps(j, indent=2, ensure_ascii=False)[:350]}</code>", [["🔙 رجوع للقائمة"]])
    else:
        tg_buttons(cid, "❌ لم يتم العثور على صناديق متاحة حالياً.", [["🔙 رجوع للقائمة"]])

def oo_do_redeem_box(cid, user):
    m = user.get("msisdn", "")
    tg_send(cid, "⏳ جاري محاولة فتح الصندوق واستلام الهدية...")
    check = oo_call_refresh(cid, oo_check_power_snake_boxes, m, user)
    if isinstance(check, dict) and check.get("success"):
        j_data = check.get("json")
        box_id = None
        if isinstance(j_data, list) and len(j_data) > 0:
            box_id = j_data[0].get("id") or j_data[0].get("uuid")
        elif isinstance(j_data, dict):
            items = j_data.get("data") or j_data.get("result") or []
            if items and isinstance(items, list):
                box_id = items[0].get("id") or items[0].get("uuid")
        
        if not box_id:
            box_id = "default"
        
        res = oo_call_refresh(cid, oo_redeem_power_snake_box, m, user, box_id)
        if isinstance(res, dict) and res.get("success"):
            tg_buttons(cid, "🎉 <b>تم فتح الصندوق بنجاح! 📦✨</b>", [["🔙 رجوع للقائمة"]])
            return
    tg_buttons(cid, "❌ <b>فشل فتح الصندوق:</b> لا توجد صناديق متاحة لفتحها حالياً.", [["🔙 رجوع للقائمة"]])

def handle(cid, text):
    try:
        text = text.strip()
        sess  = oo_get_session(cid)
        state = sess.get("state", "")
        user  = oo_get_user(cid)

        if text == "/start":
            oo_clear_session(cid)
            if user and user.get("access_token") and oo_check_session(user, cid):
                return oo_menu(cid)
            oo_set_session(cid, {"state": "awaiting_phone"})
            return tg_send(cid, "👋 مرحباً بك في بوت أورييدو الاحترافي 🇩🇿\nأرسل رقم هاتف أوريدو الخاص بك (05XXXXXXXX) 📱:")

        if state == "awaiting_phone":
            dg = "".join(c for c in text if c.isdigit())
            if not re.match(r"^05\d{8}$", dg):
                return tg_send(cid, "❌ رقم غير صحيح. أرسل رقماً يبدأ بـ 05 (مثال: 0550123456):")
            msisdn = "213" + dg[1:]
            wait = _check_otp_cooldown(cid)
            if wait > 0:
                return tg_send(cid, f"⚠️ <b>الرجاء الانتظار {wait} ثانية للحماية من حظر الـ IP.</b>", parse_mode="HTML")
            oo_set_session(cid, {"state": "awaiting_otp", "msisdn": msisdn})
            tg_buttons(cid, "✅ تم استلام الرقم!\n📩 جاري إرسال رمز التحقق (OTP)...", [["📱 تغيير الرقم"]])
            
            def _bg():
                res = oo_send_otp(msisdn)
                if res.get("ok"):
                    tg_buttons(cid, "✅ تم إرسال OTP بنجاح.\nأرسل الرمز المكون من 6 أرقام هنا:", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
                else:
                    tg_buttons(cid, "⚠️ فشل إرسال الرمز، تأكد من الرقم أو حاول لاحقاً.", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
            threading.Thread(target=_bg, daemon=True).start()
            return

        if state == "awaiting_otp":
            if text == "🔄 تجديد الرمز":
                msisdn = sess.get("msisdn")
                if not msisdn:
                    oo_set_session(cid, {"state": "awaiting_phone"})
                    return tg_send(cid, "📱 أرسل رقم هاتفك أولاً:")
                tg_send(cid, "⏳ جاري إعادة إرسال الرمز...")
                def _bg2():
                    res = oo_send_otp(msisdn)
                    if res.get("ok"):
                        tg_buttons(cid, "✅ تم إعادة إرسال الرمز.", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
                    else:
                        tg_buttons(cid, "⚠️ فشل إعادة الإرسال، انتظر قليلاً.", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
                threading.Thread(target=_bg2, daemon=True).start()
                return
            if text == "📱 تغيير الرقم":
                oo_clear_session(cid)
                oo_set_session(cid, {"state": "awaiting_phone"})
                return tg_send(cid, "📱 أرسل رقم هاتفك الجديد:")
            
            if not text.isdigit() or len(text) != 6:
                return tg_buttons(cid, "❌ رمز OTP يجب أن يكون 6 أرقام صحيحة.", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
            
            dev = oo_get_device(cid)
            res = oo_verify_otp(sess.get("msisdn"), text, dev)
            if res == "wrong_otp":
                return tg_buttons(cid, "❌ الرمز خاطئ. تأكد وأعد إرساله:", [["🔄 تجديد الرمز", "📱 تغيير الرقم"]])
            if not res:
                return tg_send(cid, "❌ عذراً، سيرفر أورييدو غير متاح حالياً.")
            
            oo_save_user(cid, {"msisdn": sess.get("msisdn"), **res})
            oo_clear_session(cid)
            tg_send(cid, "🎉 تم تسجيل الدخول وحفظ الجلسة بنجاح!")
            return oo_menu(cid)

        if not user or not user.get("access_token"):
            oo_set_session(cid, {"state": "awaiting_phone"})
            return tg_send(cid, "👋 مرحباً بك!\nأرسل رقم أوريدو (05XXXXXXXX):")

        if text == "🛒 العروض المتوفرة":      return oo_offers_menu(cid)
        if text == "🎁 الهدية اليومية":      return threading.Thread(target=oo_do_daily_gift, args=(cid, user), daemon=True).start()
        if text == "🎁 التحقق من الصناديق":  return threading.Thread(target=oo_do_check_boxes, args=(cid, user), daemon=True).start()
        if text == "📦 فتح الصندوق":         return threading.Thread(target=oo_do_redeem_box, args=(cid, user), daemon=True).start()
        if text == "👻 تفعيل Snapchat":      return threading.Thread(target=oo_do_snapchat, args=(cid, user), daemon=True).start()
        
        if text == "📶 1G - 20DA":           return threading.Thread(target=oo_do_activation, args=(cid, user, "1G_20DA", "عرض 1G - 20DA"), daemon=True).start()
        if text == "🎁 عرض 2G مجاناً":       return threading.Thread(target=oo_do_activation, args=(cid, user, "BTL_24H_DATA_Free_2Go", "عرض 2G مجاناً (24 ساعة)"), daemon=True).start()

        if text == "🚪 خروج":
            oo_delete_user(cid); oo_clear_session(cid)
            return tg_send(cid, "✅ تم تسجيل الخروج بنجاح. أرسل /start للبدء من جديد.")
        if text == "🔙 رجوع للقائمة":         return oo_menu(cid)
        
        oo_menu(cid)
    except Exception as e:
        logger.exception(f"handle error: {e}")
        oo_menu(cid)

def get_updates(offset=None):
    try:
        r = _tg_session.get(f"{TELEGRAM_API}/getUpdates",
                            params={"timeout": 15, "offset": offset}, timeout=(5, 20))
        return r.json()
    except: return None

def polling_loop():
    logger.info("🚀 Ooredoo Telegram Bot Started Successfully...")
    try:
        _tg_session.get(f"{TELEGRAM_API}/deleteWebhook", params={"drop_pending_updates": "true"}, timeout=5)
    except Exception as e:
        logger.warning(f"⚠️ تجاهل خطأ شبكة البدء: {e}")
        
    offset = None
    while True:
        try:
            data = get_updates(offset)
            if data and data.get("ok"):
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    if msg := upd.get("message"):
                        cid  = msg.get("chat", {}).get("id")
                        text = msg.get("text", "").strip()
                        if cid and text:
                            if frm := msg.get("from"):
                                oo_save_user(cid, {"first_name": frm.get("first_name"),
                                                   "username": frm.get("username")})
                            threading.Thread(target=handle, args=(cid, text), daemon=True).start()
        except Exception as e:
            logger.debug(f"network error: {e}")
            time.sleep(3)

def run():
    _load_from_disk()
    polling_loop()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        with _lock: _do_save()
