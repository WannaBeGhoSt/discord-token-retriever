import base64
import json
import sys
import time
import uuid
import random
from curl_cffi import requests
import ui

API_BASE = "https://discord.com/api/v9"
LOGIN_URL = f"{API_BASE}/auth/login"
MFA_TOTP_URL = f"{API_BASE}/auth/mfa/totp"
EXPERIMENTS_URL = f"{API_BASE}/experiments"
SCIENCE_URL = f"{API_BASE}/science"
USERS_ME_URL = f"{API_BASE}/users/@me"
LOGIN_PAGE = "https://discord.com/login"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
DEVICE_ID = str(uuid.uuid4())

def ghostydelay(min_s=0.6, max_s=1.8):
    time.sleep(random.uniform(min_s, max_s))

def build_headers(fingerprint: str, session: requests.Session) -> dict:
    super_props = {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": USER_AGENT,
        "browser_version": "124.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": 295386,
        "client_event_source": None
    }
    
    x_super_properties = base64.b64encode(json.dumps(super_props).encode()).decode()
    
    return {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/login",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
        "X-Discord-Device-Id": DEVICE_ID,
        "X-Super-Properties": x_super_properties,
        "X-Fingerprint": fingerprint
    }

def get_fingerprint(session: requests.Session) -> str:
    res = session.get(EXPERIMENTS_URL, impersonate="chrome124")
    if res.status_code != 200:
        ui.log_error(f"Failed to fetch fingerprint from experiments: HTTP {res.status_code}")
        ui.log_support_prompt()
        sys.exit(1)
    fp = res.json().get("fingerprint")
    ui.log_step("FINGERPRINT", f"Extracted fingerprint: {fp[:24]}...")
    return fp

def seed_cookies(session: requests.Session):
    ui.log_step("COOKIES", "Hitting login page to seed Cloudflare & Discord DUID cookies...")
    session.get(LOGIN_PAGE, impersonate="chrome124")
    ghostydelay(0.8, 1.8)

def send_science_event(session: requests.Session, headers: dict, event_type: str):
    ui.log_step("TELEMETRY", f"Emitting science telemetry event: '{event_type}'")
    payload = {
        "token": None,
        "events": [
            {
                "type": event_type,
                "properties": {
                    "client_track_event_id": str(uuid.uuid4())
                }
            }
        ]
    }
    try:
        session.post(SCIENCE_URL, json=payload, headers=headers, impersonate="chrome124")
        ghostydelay(0.4, 1.0)
    except Exception:
        pass

def fetch_user_profile(session: requests.Session, token: str) -> dict:
    try:
        res = session.get(
            USERS_ME_URL,
            headers={
                "Authorization": token,
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json"
            },
            impersonate="chrome124",
            timeout=8
        )
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def login_handleGhoSty(session: requests.Session, email: str, password: str):
    seed_cookies(session)
    
    fingerprint = get_fingerprint(session)
    headers = build_headers(fingerprint, session)
    send_science_event(session, headers, "login_page_viewed")
    
    payload = {
        "login": email,
        "password": password,
        "undelete": False,
        "login_source": None,
        "gift_code_sku_id": None
    }
    
    ui.log_step("AUTH", "Transmitting login payload with Chrome 124 TLS signature...")
    res = session.post(LOGIN_URL, json=payload, headers=headers, impersonate="chrome124")
    data = res.json()
    
    if res.status_code == 200 and "token" in data:
        return data["token"], session
        
    if data.get("mfa") and data.get("ticket"):
        ui.log_warn("Two-Factor Authentication (2FA/TOTP) required by Discord security.")
        return handle_mfa(session, headers, data["ticket"]), session
        
    if "captcha_key" in data or (res.status_code == 400 and "captcha" in str(data)):
        ui.log_error("Captcha challenge required by Discord (hCaptcha) for this IP/session.")
        ui.log_warn("To bypass, solve via Capsolver / 2Captcha or rotate proxy/IP.")
        ui.log_support_prompt()
        sys.exit(1)
        
    err_msg = data.get("message", "Invalid login or password")
    ui.log_error(f"Login failed: {err_msg}")
    if "errors" in data:
        for field, details in data["errors"].items():
            if isinstance(details, dict) and "_errors" in details:
                for err in details["_errors"]:
                    ui.log_error(f"  └─ {field}: {err.get('message', 'Validation error')}")
    ui.log_support_prompt()
    sys.exit(1)

def handle_mfa(session: requests.Session, headers: dict, ticket: str) -> str:
    print("")
    mfa_code = ui.prompt_input("Enter 6-digit TOTP / Backup Code")
    ui.log_step("MFA", "Submitting TOTP verification code with session ticket...")
    
    payload = {
        "code": mfa_code,
        "ticket": ticket,
        "login_source": None,
        "gift_code_sku_id": None
    }
    
    res = session.post(MFA_TOTP_URL, json=payload, headers=headers, impersonate="chrome124")
    data = res.json()
    
    if res.status_code == 200 and "token" in data:
        return data["token"]
        
    ui.log_error(f"2FA Verification Failed: {data.get('message', 'Invalid code or ticket expired')}")
    ui.log_support_prompt()
    sys.exit(1)

def main():
    ui.clear_screen()
    ui.render_header(device_id=DEVICE_ID)
    email = ui.prompt_input("Discord Email / Phone").strip()
    password = ui.prompt_input("Discord Password")
    print("")
    session = requests.Session()
    token, authed_session = login_handleGhoSty(session, email, password)
    ui.log_success("Account authenticated successfully!")
    user_data = fetch_user_profile(authed_session, token)
    ui.render_token_card(token=token, user_data=user_data, device_id=DEVICE_ID)
    if ui.copy_to_clipboard(token):
        ui.log_step("CLIPBOARD", "Token copied to Windows clipboard!", bg_color=(168, 85, 247), fg_color=(255, 255, 255))
        
    if ui.save_token_to_file(token, user_data):
        ui.log_step("SAVED", "Token saved to token.txt", bg_color=(16, 185, 129), fg_color=(0, 0, 0))
        
    print("")

if __name__ == "__main__":
    main()