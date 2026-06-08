import os
import re
import json
import time
import pickle
import threading
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import telebot
from telebot import types
from urllib.parse import urlencode


CONFIG_FILE = "config.json"
COOKIES_FILE = "cookies.pkl"
LAST_SEEN_FILE = "last_seen.json"
ADMIN_CONFIG_FILE = "admin_config.json"


if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
else:
    cfg = {}


TELEGRAM_TOKEN = cfg.get("telegram_token") or os.environ.get("TELEGRAM_TOKEN")
ADMIN_USERNAME = cfg.get("admin_username") or os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = cfg.get("admin_password") or os.environ.get("ADMIN_PASSWORD")


ADMIN_IDS = cfg.get("admin_ids", [])

if not TELEGRAM_TOKEN:
    raise SystemExit("❌ ضع telegram_token في config.json أو في متغيرات البيئة")


def load_admin_config():
    
    if os.path.exists(ADMIN_CONFIG_FILE):
        try:
            with open(ADMIN_CONFIG_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except:
            pass
    
    return {
        "otp_groups": cfg.get("otp_groups", ["-1004290930965"]),
        "button1_text": "Developer,
        "button1_url": "https://t.me/prince_ACTIVE1",
        "button2_text": "💬 numbers",
        "button2_url": "https://t.me/yoursupport",
        "imssms_username": cfg.get("admin_username", ""),
        "imssms_password": cfg.get("admin_password", "")
    }

def save_admin_config(config):
    
    try:
        with open(ADMIN_CONFIG_FILE, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"⚠️ خطأ حفظ admin_config: {e}")
        return False

admin_config = load_admin_config()


COUNTRY_MAP = {
    
    "Egypt": "🇪🇬", "Palestine": "🇵🇸", "Saudi": "🇸🇦", "UAE": "🇦🇪", 
    "Yemen": "🇾🇪", "Jordan": "🇯🇴", "Lebanon": "🇱🇧", "Syria": "🇸🇾",
    "Algeria": "🇩🇿", "Morocco": "🇲🇦", "Tunisia": "🇹🇳", "Libya": "🇱🇾",
    "Iraq": "🇮🇶", "Sudan": "🇸🇩", "Somalia": "🇸🇴", "Mauritania": "🇲🇷",
    "Oman": "🇴🇲", "Kuwait": "🇰🇼", "Qatar": "🇶🇦", "Bahrain": "🇧🇭",
    "Djibouti": "🇩🇯", "Comoros": "🇰🇲",
    
    
    "India": "🇮🇳", "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Afghanistan": "🇦🇫",
    "China": "🇨🇳", "Japan": "🇯🇵", "Korea": "🇰🇷", "Thailand": "🇹🇭",
    "Vietnam": "🇻🇳", "Philippines": "🇵🇭", "Indonesia": "🇮🇩", "Malaysia": "🇲🇾",
    "Singapore": "🇸🇬", "Myanmar": "🇲🇲", "Cambodia": "🇰🇭", "Laos": "🇱🇦",
    "Nepal": "🇳🇵", "Sri Lanka": "🇱🇰", "Maldives": "🇲🇻", "Bhutan": "🇧🇹",
    "Mongolia": "🇲🇳", "Taiwan": "🇹🇼", "Hong Kong": "🇭🇰", "Macau": "🇲🇴",
    "Uzbekistan": "🇺🇿", "Kazakhstan": "🇰🇿", "Turkmenistan": "🇹🇲",
    "Kyrgyzstan": "🇰🇬", "Tajikistan": "🇹🇯", "Azerbaijan": "🇦🇿",
    "Armenia": "🇦🇲", "Georgia": "🇬🇪", "Turkey": "🇹🇷", "Iran": "🇮🇷",
    "Israel": "🇮🇱",
    
    
    "Nigeria": "🇳🇬", "Ethiopia": "🇪🇹", "Kenya": "🇰🇪", "Tanzania": "🇹🇿",
    "Uganda": "🇺🇬", "Ghana": "🇬🇭", "Cameroon": "🇨🇲", "Senegal": "🇸🇳",
    "Mali": "🇲🇱", "Niger": "🇳🇪", "Chad": "🇹🇩", "Angola": "🇦🇴",
    "Mozambique": "🇲🇿", "Madagascar": "🇲🇬", "Malawi": "🇲🇼", "Zambia": "🇿🇲",
    "Zimbabwe": "🇿🇼", "Botswana": "🇧🇼", "Namibia": "🇳🇦", "South Africa": "🇿🇦",
    "Rwanda": "🇷🇼", "Burundi": "🇧🇮", "Congo": "🇨🇬", "Gabon": "🇬🇦",
    "Benin": "🇧🇯", "Togo": "🇹🇬", "Burkina Faso": "🇧🇫", "Guinea": "🇬🇳",
    "Sierra Leone": "🇸🇱", "Liberia": "🇱🇷", "Ivory Coast": "🇨🇮",
    "Central African Republic": "🇨🇫", "Eritrea": "🇪🇷", "Lesotho": "🇱🇸",
    "Swaziland": "🇸🇿", "Seychelles": "🇸🇨", "Mauritius": "🇲🇺",
    
    
    "UK": "🇬🇧", "France": "🇫🇷", "Germany": "🇩🇪", "Italy": "🇮🇹",
    "Spain": "🇪🇸", "Portugal": "🇵🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
    "Switzerland": "🇨🇭", "Austria": "🇦🇹", "Poland": "🇵🇱", "Ukraine": "🇺🇦",
    "Russia": "🇷🇺", "Greece": "🇬🇷", "Romania": "🇷🇴", "Czech": "🇨🇿",
    "Hungary": "🇭🇺", "Sweden": "🇸🇪", "Norway": "🇳🇴", "Finland": "🇫🇮",
    "Denmark": "🇩🇰", "Ireland": "🇮🇪", "Croatia": "🇭🇷", "Serbia": "🇷🇸",
    "Bulgaria": "🇧🇬", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Lithuania": "🇱🇹",
    "Latvia": "🇱🇻", "Estonia": "🇪🇪", "Belarus": "🇧🇾", "Moldova": "🇲🇩",
    "Albania": "🇦🇱", "Macedonia": "🇲🇰", "Bosnia": "🇧🇦", "Montenegro": "🇲🇪",
    "Iceland": "🇮🇸", "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "Cyprus": "🇨🇾",
    
    
    "USA": "🇺🇸", "Canada": "🇨🇦", "Mexico": "🇲🇽", "Brazil": "🇧🇷",
    "Argentina": "🇦🇷", "Chile": "🇨🇱", "Colombia": "🇨🇴", "Peru": "🇵🇪",
    "Venezuela": "🇻🇪", "Ecuador": "🇪🇨", "Bolivia": "🇧🇴", "Paraguay": "🇵🇾",
    "Uruguay": "🇺🇾", "Guatemala": "🇬🇹", "Honduras": "🇭🇳", "Nicaragua": "🇳🇮",
    "Costa Rica": "🇨🇷", "Panama": "🇵🇦", "Cuba": "🇨🇺", "Jamaica": "🇯🇲",
    "Haiti": "🇭🇹", "Dominican Republic": "🇩🇴", "Trinidad": "🇹🇹",
    "Bahamas": "🇧🇸", "Barbados": "🇧🇧", "Belize": "🇧🇿", "Guyana": "🇬🇾",
    "Suriname": "🇸🇷", "El Salvador": "🇸🇻",
    
    
    "Australia": "🇦🇺", "New Zealand": "🇳🇿", "Papua New Guinea": "🇵🇬",
    "Fiji": "🇫🇯", "Samoa": "🇼🇸", "Tonga": "🇹🇴", "Vanuatu": "🇻🇺",
}


bot = telebot.TeleBot(TELEGRAM_TOKEN)


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "Accept-Language": "ar-EG,ar;q=0.6"
})

BASE = "https://www.imssms.org"
LOGIN_PAGE = BASE + "/login"
SIGNIN_URL = BASE + "/signin"
DASHBOARD_URL = BASE + "/client/SMSDashboard"
DATA_ENDPOINT = BASE + "/client/res/data_smscdr.php"


def log(msg):
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def is_admin(user_id):
    
    return user_id in ADMIN_IDS


def get_last_seen():
    
    if not os.path.exists(LAST_SEEN_FILE):
        return {}
    try:
        with open(LAST_SEEN_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            
            if "last_timestamp" not in data:
                data["last_timestamp"] = None
            return data
    except:
        return {"last_timestamp": None}

def save_last_seen(d):
    
    try:
        with open(LAST_SEEN_FILE, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠️ خطأ حفظ last_seen: {e}")


def save_cookies():
    try:
        with open(COOKIES_FILE, "wb") as fh:
            pickle.dump(session.cookies.get_dict(), fh)
    except Exception as e:
        log(f"⚠️ خطأ حفظ الكوكيز: {e}")

def load_cookies():
    if not os.path.exists(COOKIES_FILE):
        return False
    try:
        with open(COOKIES_FILE, "rb") as fh:
            data = pickle.load(fh)
            session.cookies.update(data)
        return True
    except:
        return False


def is_session_valid():
    try:
        r = session.get(DASHBOARD_URL, timeout=10, allow_redirects=True)
        txt = (r.text or "").lower()
        return ("logout" in txt) or r.url.endswith("/client/SMSDashboard")
    except:
        return False


def login_admin(username, password):
    try:
        # جلب صفحة تسجيل الدخول
        r = session.get(LOGIN_PAGE, timeout=12)
        if r.status_code != 200:
            log(f"❌ فشل جلب صفحة تسجيل الدخول ({r.status_code})")
            return False

        soup = BeautifulSoup(r.text, "html.parser")
        
        # استخراج etkk من الـ input المخفي
        etkk_input = soup.find("input", {"name": "etkk"})
        etkk = etkk_input["value"] if etkk_input and etkk_input.has_attr("value") else None
        
        # استخراج الكابتشا المتغيرة
        capt_answer = None
        
        # البحث عن نص الكابتشا في الصفحة
        # النص يكون مثل: "What is 6 + 10 = ?" أو "What is 8 + 3 = ?"
        captcha_pattern = r'What is\s+(\d+)\s*\+\s*(\d+)\s*=\s*\?'
        match = re.search(captcha_pattern, r.text)
        
        if match:
            num1 = int(match.group(1))
            num2 = int(match.group(2))
            capt_answer = str(num1 + num2)
            log(f"🔢 تم حل الكابتشا: {num1} + {num2} = {capt_answer}")
        else:
            # محاولة بديلة: البحث في أي عنصر يحتوي على الأرقام
            for div in soup.find_all("div", class_="row"):
                text = div.get_text(strip=True)
                numbers = re.findall(r'(\d+)\s*\+\s*(\d+)', text)
                if numbers:
                    num1, num2 = int(numbers[0][0]), int(numbers[0][1])
                    capt_answer = str(num1 + num2)
                    log(f"🔢 تم حل الكابتشا بالطريقة البديلة: {num1} + {num2} = {capt_answer}")
                    break
        
        if not capt_answer:
            log("⚠️ لم يتم العثور على كابتشا قابلة للحل.")
            log(f"📄 جزء من الصفحة: {r.text[:1000]}")
            return False

        # بناء البيانات للإرسال
        payload = {
            "username": username, 
            "password": password, 
            "capt": capt_answer
        }
        if etkk: 
            payload["etkk"] = etkk
            log(f"📝 etkk found: {etkk}")
        
        log(f"🔑 محاولة تسجيل الدخول للمستخدم: {username}")
        
        # إرسال طلب تسجيل الدخول
        post = session.post(SIGNIN_URL, data=payload, timeout=12, allow_redirects=True)
        
        log(f"📡 رد تسجيل الدخول: Status={post.status_code}, URL={post.url}")
        
        # التحقق من نجاح تسجيل الدخول
        text = (post.text or "").lower()
        url = post.url.lower()
        
        # طرق التحقق من النجاح
        if post.status_code in (200, 302):
            if "dashboard" in url or "client" in url or "smsdashboard" in url:
                save_cookies()
                log("✔️ تسجيل الدخول ناجح.")
                return True
            elif "login" not in url and "signin" not in url:
                save_cookies()
                log("✔️ تسجيل الدخول ناجح (تم التوجيه).")
                return True
            else:
                log(f"❌ فشل تسجيل الدخول. تم البقاء في صفحة الدخول.")
                log(f"📄 جزء من الرد: {text[:500]}")
                return False
        
        log(f"❌ فشل تسجيل الدخول. Status code: {post.status_code}")
        return False
        
    except Exception as e:
        log(f"⚠️ خطأ أثناء تسجيل الدخول: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_sesskey_from_page():
    """
    الحصول على sesskey من صفحة SMSCDRReports
    """
    try:
        # جلب صفحة SMSCDRReports
        url = BASE + "/client/SMSCDRStats"
        log(f"🔍 محاولة جلب sesskey من {url}")
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        # طباعة جزء من الصفحة للتصحيح
        log(f"📄 تم جلب الصفحة بنجاح، حجمها: {len(response.text)} حرف")
        
        # البحث عن sesskey في محتوى الصفحة بطرق متعددة
        sesskey = None
        
        # الطريقة 1: البحث في الروابط أو الـ iframes
        soup = BeautifulSoup(response.text, "html.parser")
        
        # البحث في جميع الـ script tags
        for script in soup.find_all("script"):
            if script.string:
                match = re.search(r'sesskey\s*[=:]\s*["\']([A-Za-z0-9+\/=]+)["\']', script.string)
                if match:
                    sesskey = match.group(1)
                    log(f"✅ تم العثور على sesskey في script: {sesskey}")
                    break
        
        # الطريقة 2: البحث في الـ input المخفية
        if not sesskey:
            sesskey_input = soup.find("input", {"name": "sesskey"})
            if sesskey_input and sesskey_input.get("value"):
                sesskey = sesskey_input["value"]
                log(f"✅ تم العثور على sesskey في input: {sesskey}")
        
        # الطريقة 3: البحث المباشر في النص
        if not sesskey:
            # البحث عن pattern: sesskey=XXXXX
            match = re.search(r'sesskey[=:]\s*([A-Za-z0-9+\/=]+)', response.text)
            if match:
                sesskey = match.group(1)
                log(f"✅ تم العثور على sesskey في النص: {sesskey}")
        
        # الطريقة 4: البحث في الـ URLs داخل الصفحة
        if not sesskey:
            # البحث في الروابط التي تحتوي على sesskey
            url_pattern = r'[?&]sesskey=([A-Za-z0-9+\/=]+)'
            match = re.search(url_pattern, response.text)
            if match:
                sesskey = match.group(1)
                log(f"✅ تم العثور على sesskey في URL: {sesskey}")
        
        if sesskey:
            return sesskey
        else:
            # طباعة أول 500 حرف من الصفحة للتصحيح
            log("⚠️ لم يتم العثور على sesskey في الصفحة")
            log(f"📄 بداية الصفحة: {response.text[:500]}")
            return None
            
    except Exception as e:
        log(f"⚠️ خطأ في الحصول على sesskey: {e}")
        return None

def build_data_url(iDisplayLength=1000, start_from_datetime=None, sesskey=None):
    """
    بناء رابط API لجلب البيانات باستخدام المعاملات الجديدة (sesskey)
    """
    from datetime import timedelta
    
    now = datetime.now()
    end_time = now
    
    # تحديد وقت البداية
    if start_from_datetime:
        start_time = start_from_datetime - timedelta(minutes=1)
        log(f"📌 البدء من آخر رسالة محفوظة: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # جلب من بداية اليوم الحالي
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        log(f"🆕 لا توجد رسائل محفوظة - جلب من بداية اليوم")
    
    # تحديد النطاق الزمني
    fdate1 = start_time.strftime("%Y-%m-%d %H:%M:%S")
    fdate2 = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # المعاملات المطلوبة حسب الـ curl الذي يعمل
    params = {
        "fdate1": fdate1,
        "fdate2": fdate2,
        "frange": "",
        "fnum": "",
        "fcli": "",
        "fgdate": "",
        "fgmonth": "",
        "fgrange": "",
        "fgnumber": "",
        "fgcli": "",
        "fg": "0",
        "sesskey": sesskey if sesskey else "",
        "sEcho": "1",
        "iColumns": "7",
        "sColumns": ",,,,,,",
        "iDisplayStart": "0",
        "iDisplayLength": str(iDisplayLength),
        "mDataProp_0": "0",
        "sSearch_0": "",
        "bRegex_0": "false",
        "bSearchable_0": "true",
        "bSortable_0": "true",
        "mDataProp_1": "1",
        "sSearch_1": "",
        "bRegex_1": "false",
        "bSearchable_1": "true",
        "bSortable_1": "true",
        "mDataProp_2": "2",
        "sSearch_2": "",
        "bRegex_2": "false",
        "bSearchable_2": "true",
        "bSortable_2": "true",
        "mDataProp_3": "3",
        "sSearch_3": "",
        "bRegex_3": "false",
        "bSearchable_3": "true",
        "bSortable_3": "true",
        "mDataProp_4": "4",
        "sSearch_4": "",
        "bRegex_4": "false",
        "bSearchable_4": "true",
        "bSortable_4": "true",
        "mDataProp_5": "5",
        "sSearch_5": "",
        "bRegex_5": "false",
        "bSearchable_5": "true",
        "bSortable_5": "true",
        "mDataProp_6": "6",
        "sSearch_6": "",
        "bRegex_6": "false",
        "bSearchable_6": "true",
        "bSortable_6": "true",
        "sSearch": "",
        "bRegex": "false",
        "iSortCol_0": "0",
        "sSortDir_0": "desc",
        "iSortingCols": "1",
        "_": str(int(time.time() * 1000))
    }
    
    # طباعة الرابط للتصحيح
    full_url = DATA_ENDPOINT + "?" + urlencode(params)
    log(f"📅 جلب الرسائل من {fdate1} إلى {fdate2} (الحد: {iDisplayLength})")
    log(f"🔗 الرابط: {full_url[:200]}...")  # طباعة أول 200 حرف من الرابط
    
    return full_url

def parse_datetime(date_str):
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except:
            return None

def fetch_latest_messages(count=1000, start_from_datetime=None):
    """
    جلب الرسائل باستخدام المعاملات الجديدة
    """
    # الحصول على sesskey أولاً
    sesskey = get_sesskey_from_page()
    if not sesskey:
        log("⚠️ فشل الحصول على sesskey، لا يمكن جلب البيانات")
        return []
    
    url = build_data_url(count, start_from_datetime, sesskey)
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE + "/client/SMSCDRStats"
    }
    
    try:
        r = session.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        
        data = r.json()
        
        # التحقق من وجود البيانات
        if not data.get("aaData"):
            log("⚠️ الرد لا يحتوي على بيانات (aaData فارغ).")
            return []
        
        valid_rows = []
        for row in data["aaData"]:
            # تجاهل الصفوف التي لا تحتوي على بيانات حقيقية
            # الصفوف الصحيحة يجب أن تحتوي على التاريخ والرقم والرسالة
            if len(row) >= 6 and isinstance(row[0], str) and ':' in row[0]:
                # التحقق من أن الحقل الأول هو تاريخ (يحتوي على :)
                valid_rows.append(row)
            else:
                # هذا غالباً صف إحصائي أو غير صالح
                log(f"⚠️ تم تجاهل صف غير صالح: {row[:3] if len(row) > 0 else row}")
        
        if not valid_rows:
            log("⚠️ لا توجد صفوف صالحة بعد التصفية.")
            return []
        
        # ترتيب حسب الوقت (الأحدث أولاً)
        rows_with_time = []
        for row in valid_rows:
            dt = parse_datetime(row[0])
            if dt:
                rows_with_time.append((dt, row))
        
        rows_with_time.sort(key=lambda x: x[0], reverse=True)
        sorted_rows = [row for dt, row in rows_with_time]
        
        log(f"✅ تم جلب {len(sorted_rows)} رسالة صالحة")
        
        # عرض أحدث 10 رسائل
        if sorted_rows:
            log(f"📊 أحدث 10 رسائل:")
            for i, row in enumerate(sorted_rows[:10]):
                dt = parse_datetime(row[0])
                phone = row[2] if len(row) > 2 else "N/A"
                service = row[3] if len(row) > 3 else "N/A"
                msg_preview = row[5][:50] if len(row) > 5 else "N/A"
                log(f"  {i+1}. {row[0]} | {phone} | {service} | {msg_preview}")
        
        return sorted_rows
        
    except requests.exceptions.RequestException as e:
        log(f"⚠️ خطأ HTTP/شبكة: {e}")
    except json.JSONDecodeError as e:
        log(f"⚠️ فشل تحليل JSON: {e}")
        if os.path.exists(COOKIES_FILE):
            os.remove(COOKIES_FILE)
    except Exception as e:
        log(f"⚠️ fetch_latest_messages خطأ عام: {e}")
    
    return []


OTP_RE = re.compile(r"\b\d{3,8}\b")

def extract_otp(msg):
    
    match = re.search(r"\b(\d{3,8})\b", msg)
    if match:
        return match.group(1)
    return None


def get_country_info(country_name):
    
    if not country_name:
        return "Unknown", "🏳️"
    
    
    flag = COUNTRY_MAP.get(country_name)
    if flag:
        return country_name, flag
    

    for key, val in COUNTRY_MAP.items():
        if country_name.startswith(key):
            return key, val
    
    
    for key, val in COUNTRY_MAP.items():
        if key.lower() in country_name.lower() or country_name.lower() in key.lower():
            return key, val
    
    return country_name, "🏳️"


def mask_phone_number(phone):
    """
    عرض رقم الهاتف بالكامل بدون إخفاء
    """
    if not phone:
        return "N/A"
    return phone  # إرجاع الرقم كاملاً كما هو

def mask_service_name(service):
    
    if not service or len(service) <= 1:
        return service
    
    first_letter = service[0].upper()
    stars = "*" * (len(service) - 1)
    return f"{first_letter}{stars}"


def parse_row(row):
    try:
    
        t = row[0] if len(row) > 0 else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        country_net = row[1] if len(row) > 1 else "Unknown"
        phone = row[2] if len(row) > 2 else "N/A"
        app = row[3] if len(row) > 3 else "SMS"
        client = row[4] if len(row) > 4 else ""
        msg = row[5] if len(row) > 5 else ""
        
        
        country_name_match = re.search(r'\b([A-Za-z\s]+)\b', str(country_net))
        country_only = country_name_match.group(1).strip().split()[0] if country_name_match else "Unknown"
        
        
        server_match = re.search(r'\b[A-Za-z]+\b.*?\b([A-Za-z]+)\b', str(country_net))
        server_name = server_match.group(1)[0] if server_match and len(server_match.groups()) > 0 else "S"
        
        return {
            "time": t,
            "country_net": country_net,
            "country_only": country_only,
            "server": server_name,
            "phone": phone,
            "app": app,
            "client": client,
            "message": msg,
            "otp": extract_otp(msg or "")
        }
    except Exception as e:
        log(f"⚠️ خطأ في parse_row: {e}")
        return None


def build_telegram_text(parsed):
    
    country_name, flag = get_country_info(parsed.get("country_only", "Unknown"))
    t = parsed.get("time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app = parsed.get("app") or "SMS"
    masked_app = mask_service_name(app)
    phone = parsed.get("phone") or "N/A"
    # تم حذف الإخفاء - عرض الرقم كاملاً
    full_phone = mask_phone_number(phone)  # الآن ترجع الرقم كاملاً
    server = parsed.get("server", "S")
    
    lines = []
    lines.append(f'<blockquote>⏰ Time: {t}</blockquote>')
    lines.append(f'<blockquote>🌍 Country: {country_name} {flag}</blockquote>')
    lines.append(f'<blockquote>⚙️ Service: {masked_app}</blockquote>')
    lines.append(f'<blockquote>☎️ Number: {full_phone}</blockquote>')
    
    return "\n".join(lines)


def send_to_telegram(text):
    
    try:
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(
            admin_config.get("button1_text", "Button 1"),
            url=admin_config.get("button1_url", "https://t.me/telegram")
        )
        btn2 = types.InlineKeyboardButton(
            admin_config.get("button2_text", "Button 2"),
            url=admin_config.get("button2_url", "https://t.me/telegram")
        )
        markup.add(btn1, btn2)
        
        
        otp_groups = admin_config.get("otp_groups", [])
        for group_id in otp_groups:
            try:
                bot.send_message(
                    group_id,
                    text,
                    parse_mode="HTML",
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
                log(f"✅ تم الإرسال إلى المجموعة: {group_id}")
            except Exception as e:
                log(f"⚠️ خطأ إرسال للمجموعة {group_id}: {e}")
    except Exception as e:
        log(f"⚠️ خطأ عام في send_to_telegram: {e}")


def watcher(interval=16):
    
    log(f"🔍 Advanced Watcher started - checking every {interval}s")
    log(f"📡 Fetching up to 1000 messages per check for maximum accuracy")
    
    last = get_last_seen()
    if last is None:
        last = {}
    last_timestamp = last.get("last_timestamp")
    
    
    if last_timestamp:
        try:
            last_dt = datetime.fromisoformat(last_timestamp)
            log(f"📅 آخر رسالة تم إرسالها: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            last_dt = None
    else:
        last_dt = None
        log("🆕 لا توجد رسائل سابقة - سيتم إرسال الأحدث فقط")
    
    while True:
        try:
           
            if not load_cookies() or not is_session_valid():
                log("⚠️ الجلسة غير صالحة. محاولة تسجيل الدخول...")
                username = admin_config.get("imssms_username", ADMIN_USERNAME)
                password = admin_config.get("imssms_password", ADMIN_PASSWORD)
                
                if not login_admin(username, password):
                    log("⚠️ فشل تسجيل الدخول — المحاولة لاحقًا.")
                    time.sleep(interval)
                    continue

            
            rows = fetch_latest_messages(1000, last_dt)
            
            if not rows:
                log("🔁 لا توجد رسائل صالحة.")
                time.sleep(interval)
                continue
            
             
            new_messages = []
            newest_dt = None
            
            for row in rows:
                dt = parse_datetime(row[0])
                if not dt:
                    continue
                
                
                if newest_dt is None or dt > newest_dt:
                    newest_dt = dt
                
                
                if last_dt is None:
                    if newest_dt and dt == newest_dt:
                        new_messages.append(row)
                    continue
                
               
                if dt > last_dt:
                    new_messages.append(row)
            
           
            new_messages.reverse()
            
            if new_messages:
                log(f"✨ تم العثور على {len(new_messages)} رسالة جديدة!")
                
                for row in new_messages:
                    parsed = parse_row(row)
                    if parsed:
                        text = build_telegram_text(parsed)
                        msg_time = parsed.get('time', 'Unknown')
                        log(f"→ إرسال رسالة: {msg_time} | {parsed['phone']}")
                        send_to_telegram(text)
                        time.sleep(0.5)  
                
               
                if newest_dt:
                    last["last_timestamp"] = newest_dt.isoformat()
                    save_last_seen(last)
                    last_dt = newest_dt
                    log(f"✅ تم تحديث آخر رسالة: {newest_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                if last_dt:
                    log(f"🔁 لا توجد رسائل جديدة (آخر رسالة: {last_dt.strftime('%H:%M:%S')})")
                else:
                    log("🔁 لا توجد رسائل جديدة.")
                
        except Exception as e:
            log(f"❌ خطأ داخل watcher: {e}")
            import traceback
            traceback.print_exc()
            
        time.sleep(interval)


user_states = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    
    if not is_admin(user_id):
        
        return
    
    
    show_admin_panel(message.chat.id)

def show_admin_panel(chat_id):
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("🔘 تغيير الأزرار", callback_data="change_buttons")
    btn2 = types.InlineKeyboardButton("👥 إدارة مجموعات OTP", callback_data="manage_otp_groups")
    btn3 = types.InlineKeyboardButton("🔐 تغيير بيانات الدخول", callback_data="change_credentials")
    btn4 = types.InlineKeyboardButton("🧪 اختبار الدخول", callback_data="test_login")
    btn5 = types.InlineKeyboardButton("📊 الإحصائيات", callback_data="show_stats")
    btn6 = types.InlineKeyboardButton("ℹ️ معلومات البوت", callback_data="bot_info")
    btn7 = types.InlineKeyboardButton("🔄 إعادة تحميل الإعدادات", callback_data="reload_config")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    
    text = """
╔══════════════════════╗
   🎛️ <b>لوحة التحكم الرئيسية</b>
╚══════════════════════╝

مرحباً بك في لوحة تحكم البوت!
اختر أحد الخيارات التالية:

🔘 <b>تغيير الأزرار</b>: تعديل نصوص وروابط الأزرار
👥 <b>إدارة مجموعات OTP</b>: إضافة أو حذف مجموعات
🔐 <b>تغيير بيانات الدخول</b>: تحديث اسم المستخدم والباسورد
🧪 <b>اختبار الدخول</b>: التحقق من صلاحية البيانات
📊 <b>الإحصائيات</b>: عرض معلومات النظام
ℹ️ <b>معلومات البوت</b>: تفاصيل عن البوت
🔄 <b>إعادة تحميل</b>: تحديث الإعدادات
"""
    
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "⛔ غير مصرح لك!")
        return
    
   
    if call.data == "change_buttons":
        show_button_settings(call.message.chat.id, call.message.message_id)
    
    elif call.data == "manage_otp_groups":
        show_otp_groups_menu(call.message.chat.id, call.message.message_id)
    
    elif call.data == "change_credentials":
        show_credentials_menu(call.message.chat.id, call.message.message_id)
    
    elif call.data == "test_login":
        test_login_action(call.message.chat.id)
    
    elif call.data == "show_stats":
        show_statistics(call.message.chat.id)
    
    elif call.data == "bot_info":
        show_bot_info(call.message.chat.id)
    
    elif call.data == "reload_config":
        reload_config_action(call.message.chat.id)
    
    elif call.data == "back_to_main":
        show_admin_panel(call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    
    elif call.data == "change_btn1_text":
        bot.send_message(call.message.chat.id, "📝 أرسل النص الجديد للزر الأول:")
        user_states[user_id] = "awaiting_btn1_text"
    
    elif call.data == "change_btn1_url":
        bot.send_message(call.message.chat.id, "🔗 أرسل الرابط الجديد للزر الأول:")
        user_states[user_id] = "awaiting_btn1_url"
    
    elif call.data == "change_btn2_text":
        bot.send_message(call.message.chat.id, "📝 أرسل النص الجديد للزر الثاني:")
        user_states[user_id] = "awaiting_btn2_text"
    
    elif call.data == "change_btn2_url":
        bot.send_message(call.message.chat.id, "🔗 أرسل الرابط الجديد للزر الثاني:")
        user_states[user_id] = "awaiting_btn2_url"
    
    
    elif call.data == "add_otp_group":
        bot.send_message(call.message.chat.id, "➕ أرسل ID المجموعة أو @username أو رابط الدعوة:")
        user_states[user_id] = "awaiting_group_add"
    
    elif call.data == "remove_otp_group":
        show_remove_group_menu(call.message.chat.id, call.message.message_id)
    
    elif call.data == "list_otp_groups":
        list_otp_groups(call.message.chat.id)
    
    
    elif call.data == "change_username":
        bot.send_message(call.message.chat.id, "👤 أرسل اسم المستخدم الجديد:")
        user_states[user_id] = "awaiting_username"
    
    elif call.data == "change_password":
        bot.send_message(call.message.chat.id, "🔑 أرسل كلمة المرور الجديدة:")
        user_states[user_id] = "awaiting_password"
    
    
    elif call.data.startswith("remove_group_"):
        group_id = call.data.replace("remove_group_", "")
        remove_group_action(call.message.chat.id, group_id)
        show_otp_groups_menu(call.message.chat.id, call.message.message_id)
    
    bot.answer_callback_query(call.id)



def show_button_settings(chat_id, message_id=None):
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("📝 تغيير نص الزر 1", callback_data="change_btn1_text")
    btn2 = types.InlineKeyboardButton("🔗 تغيير رابط الزر 1", callback_data="change_btn1_url")
    btn3 = types.InlineKeyboardButton("📝 تغيير نص الزر 2", callback_data="change_btn2_text")
    btn4 = types.InlineKeyboardButton("🔗 تغيير رابط الزر 2", callback_data="change_btn2_url")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn_back)
    
    text = f"""
<b>⚙️ إعدادات الأزرار الحالية:</b>

<b>الزر 1:</b>
• النص: <code>{admin_config.get('button1_text', 'غير محدد')}</code>
• الرابط: <code>{admin_config.get('button1_url', 'غير محدد')}</code>

<b>الزر 2:</b>
• النص: <code>{admin_config.get('button2_text', 'غير محدد')}</code>
• الرابط: <code>{admin_config.get('button2_url', 'غير محدد')}</code>
"""
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)



def show_otp_groups_menu(chat_id, message_id=None):
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("➕ إضافة مجموعة", callback_data="add_otp_group")
    btn2 = types.InlineKeyboardButton("➖ حذف مجموعة", callback_data="remove_otp_group")
    btn3 = types.InlineKeyboardButton("📋 عرض المجموعات", callback_data="list_otp_groups")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    
    markup.add(btn1, btn2)
    markup.add(btn3)
    markup.add(btn_back)
    
    groups_count = len(admin_config.get("otp_groups", []))
    text = f"""
<b>👥 إدارة مجموعات OTP</b>

عدد المجموعات الحالية: <code>{groups_count}</code>

اختر إجراءً:
• <b>إضافة مجموعة</b>: إضافة مجموعة جديدة
• <b>حذف مجموعة</b>: إزالة مجموعة موجودة
• <b>عرض المجموعات</b>: قائمة بجميع المجموعات
"""
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def show_remove_group_menu(chat_id, message_id=None):
    
    groups = admin_config.get("otp_groups", [])
    
    if not groups:
        bot.send_message(chat_id, "⚠️ لا توجد مجموعات لحذفها!")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for group_id in groups:
        btn = types.InlineKeyboardButton(
            f"❌ حذف {group_id}",
            callback_data=f"remove_group_{group_id}"
        )
        markup.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_otp_groups")
    markup.add(btn_back)
    
    text = "<b>➖ اختر مجموعة للحذف:</b>"
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def list_otp_groups(chat_id):
    
    groups = admin_config.get("otp_groups", [])
    
    if not groups:
        bot.send_message(chat_id, "⚠️ لا توجد مجموعات مسجلة!")
        return
    
    text = "<b>📋 قائمة مجموعات OTP:</b>\n\n"
    for i, group_id in enumerate(groups, 1):
        text += f"{i}. <code>{group_id}</code>\n"
    
    bot.send_message(chat_id, text, parse_mode="HTML")

def remove_group_action(chat_id, group_id):
    
    groups = admin_config.get("otp_groups", [])
    
    if group_id in groups:
        groups.remove(group_id)
        admin_config["otp_groups"] = groups
        save_admin_config(admin_config)
        bot.send_message(chat_id, f"✅ تم حذف المجموعة: <code>{group_id}</code>", parse_mode="HTML")
    else:
        bot.send_message(chat_id, "⚠️ المجموعة غير موجودة!")



def show_credentials_menu(chat_id, message_id=None):
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("👤 تغيير اسم المستخدم", callback_data="change_username")
    btn2 = types.InlineKeyboardButton("🔑 تغيير كلمة المرور", callback_data="change_password")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    
    markup.add(btn1, btn2)
    markup.add(btn_back)
    
    current_username = admin_config.get("imssms_username", "غير محدد")
    
    text = f"""
<b>🔐 إدارة بيانات الدخول</b>

<b>اسم المستخدم الحالي:</b>
<code>{current_username}</code>

<b>كلمة المرور:</b>
<code>••••••••</code>

اختر ما تريد تعديله:
"""
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)



def test_login_action(chat_id):
    
    bot.send_message(chat_id, "🔄 جاري اختبار تسجيل الدخول...")
    
    username = admin_config.get("imssms_username", ADMIN_USERNAME)
    password = admin_config.get("imssms_password", ADMIN_PASSWORD)
    
    success = login_admin(username, password)
    
    if success:
        bot.send_message(chat_id, "✅ <b>نجح تسجيل الدخول!</b>\n\nالحساب يعمل بشكل صحيح.", parse_mode="HTML")
    else:
        bot.send_message(chat_id, "❌ <b>فشل تسجيل الدخول!</b>\n\nيرجى التحقق من بيانات الدخول.", parse_mode="HTML")


def show_statistics(chat_id):
    
    groups_count = len(admin_config.get("otp_groups", []))
    last_seen = get_last_seen()
    has_session = os.path.exists(COOKIES_FILE)
    
    last_ts = last_seen.get('last_timestamp', 'لا توجد')
    if last_ts and last_ts != 'لا توجد':
        try:
            dt = datetime.fromisoformat(last_ts)
            last_msg_display = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            last_msg_display = str(last_ts)[:20]
    else:
        last_msg_display = 'لا توجد'
    
    text = f"""
<b>📊 إحصائيات النظام</b>

<b>المجموعات:</b> {groups_count}
<b>حالة الجلسة:</b> {'🟢 نشطة' if has_session else '🔴 غير نشطة'}
<b>آخر رسالة:</b> {last_msg_display}

<b>الأزرار المفعلة:</b>
• {admin_config.get('button1_text', 'N/A')}
• {admin_config.get('button2_text', 'N/A')}

<b>الدول المدعومة:</b> {len(COUNTRY_MAP)} دولة
"""
    
    bot.send_message(chat_id, text, parse_mode="HTML")

def show_bot_info(chat_id):
    
    text = """
<b>ℹ️ معلومات البوت</b>

<b>الإصدار:</b> 2.0 Pro
<b>المطور:</b> Advanced SMS Monitor
<b>الميزات:</b>
• ✅ كشف تلقائي للدولة
• ✅ إخفاء متقدم للأرقام والخدمات
• ✅ دعم مجموعات متعددة
• ✅ لوحة تحكم شاملة
• ✅ أزرار قابلة للتخصيص
• ✅ +150 دولة مدعومة

<b>الحالة:</b> 🟢 يعمل بكفاءة
"""
    
    bot.send_message(chat_id, text, parse_mode="HTML")

def reload_config_action(chat_id):
    
    global admin_config
    admin_config = load_admin_config()
    bot.send_message(chat_id, "✅ تم إعادة تحميل الإعدادات بنجاح!")



@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    
    user_id = message.from_user.id
    
    
    if not is_admin(user_id):
        return
    
    
    state = user_states.get(user_id)
    
    if state == "awaiting_btn1_text":
        admin_config["button1_text"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, f"✅ تم تحديث نص الزر 1 إلى: <b>{message.text}</b>", parse_mode="HTML")
        user_states.pop(user_id, None)
    
    elif state == "awaiting_btn1_url":
        admin_config["button1_url"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, f"✅ تم تحديث رابط الزر 1 إلى: <code>{message.text}</code>", parse_mode="HTML")
        user_states.pop(user_id, None)
    
    elif state == "awaiting_btn2_text":
        admin_config["button2_text"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, f"✅ تم تحديث نص الزر 2 إلى: <b>{message.text}</b>", parse_mode="HTML")
        user_states.pop(user_id, None)
    
    elif state == "awaiting_btn2_url":
        admin_config["button2_url"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, f"✅ تم تحديث رابط الزر 2 إلى: <code>{message.text}</code>", parse_mode="HTML")
        user_states.pop(user_id, None)
    
    elif state == "awaiting_group_add":
        group_input = message.text.strip()
        
        # معالجة @username
        if group_input.startswith("@"):
            group_id = group_input
        # معالجة روابط t.me
        elif "t.me/" in group_input or "telegram.me/" in group_input:
            # استخراج اسم المجموعة من الرابط
            if "t.me/" in group_input:
                parts = group_input.split("t.me/")[-1].split("/")[0]
                group_id = f"@{parts}" if not parts.startswith("@") else parts
            else:
                parts = group_input.split("telegram.me/")[-1].split("/")[0]
                group_id = f"@{parts}" if not parts.startswith("@") else parts
        # معالجة ID رقمي
        elif group_input.startswith("-") or (group_input.lstrip("-").isdigit()):
            group_id = group_input
        else:
            bot.send_message(message.chat.id, "⚠️ الصيغة غير صحيحة!\n\nأمثلة صحيحة:\n• <code>-1004290930965</code>\n• <code>@channel_name</code>\n• <code>https://t.me/channel_name</code>", parse_mode="HTML")
            user_states.pop(user_id, None)
            return
        
        groups = admin_config.get("otp_groups", [])
        if group_id not in groups:
            groups.append(group_id)
            admin_config["otp_groups"] = groups
            save_admin_config(admin_config)
            bot.send_message(message.chat.id, f"✅ تم إضافة المجموعة: <code>{group_id}</code>\n\n💡 تأكد من إضافة البوت للمجموعة كمشرف!", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "⚠️ المجموعة موجودة بالفعل!")
        
        user_states.pop(user_id, None)
    
    elif state == "awaiting_username":
        admin_config["imssms_username"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, f"✅ تم تحديث اسم المستخدم إلى: <code>{message.text}</code>", parse_mode="HTML")
        user_states.pop(user_id, None)
    
    elif state == "awaiting_password":
        admin_config["imssms_password"] = message.text
        save_admin_config(admin_config)
        bot.send_message(message.chat.id, "✅ تم تحديث كلمة المرور بنجاح!", parse_mode="HTML")
        user_states.pop(user_id, None)



if __name__ == "__main__":
    
    t = threading.Thread(target=watcher, args=(16,), daemon=True)
    t.start()
    
    log("🤖 Bot and watcher running. Polling Telegram ...")
    log(f"📊 {len(COUNTRY_MAP)} countries loaded")
    log(f"👥 {len(admin_config.get('otp_groups', []))} OTP groups configured")
    
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        log("تم الإيقاف بواسطة المستخدم.")
