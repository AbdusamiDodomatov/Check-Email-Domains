import re
import time
import dns.resolver
import requests

TG_BOT_TOKEN = "" # ← Вставь сюда свой токен бота


API_GET_UPDATES = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates"
API_SEND_MESSAGE = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

EMAIL_RE = re.compile(r"^[^@]+@([^@]+\.[^@]+)$")
POLL_INTERVAL = 5  # секунды между проверками новых сообщений

def extract_domain(email):
    m = EMAIL_RE.match(email)
    return m.group(1).lower() if m else None

def check_mx(domain, timeout=5.0):
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    try:
        answers = resolver.resolve(domain, "MX")
        mxs = [(int(getattr(r,"preference",0)), str(getattr(r,"exchange","")).rstrip(".")) for r in answers]
        if mxs:
            return "домен валиден", mxs
        else:
            return "MX-записи отсутствуют или некорректны", None
    except dns.resolver.NXDOMAIN:
        return "домен отсутствует", None
    except dns.resolver.NoAnswer:
        return "MX-записи отсутствуют или некорректны", None
    except dns.resolver.NoNameservers:
        return "не найдены DNS-серверы для домена", None
    except Exception as e:
        return f"ошибка проверки: {e}", None

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    try:
        requests.post(API_SEND_MESSAGE, data=payload, timeout=10)
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

def process_message(chat_id, text):
    emails = [e.strip() for e in text.replace(",", "\n").split()]
    results = []
    for email in emails:
        domain = extract_domain(email)
        if not domain:
            results.append(f"{email}\tINVALID_EMAIL")
            continue
        status, mx = check_mx(domain)
        mx_str = ", ".join([f"{p} {h}" for p,h in mx]) if mx else "—"
        results.append(f"{email:30} {status:40} MX: {mx_str}")
    send_message(chat_id, "\n".join(results))
    print(f"Отправлено в чат {chat_id}")

def main():
    last_update_id = None
    print("Бот MX-проверки запущен. Жду новых сообщений...")
    
    while True:
        try:
            params = {"timeout":30}
            if last_update_id:
                params["offset"] = last_update_id + 1

            resp = requests.get(API_GET_UPDATES, timeout=35, params=params)
            updates = resp.json().get("result", [])
            
            for upd in updates:
                if "message" not in upd:
                    continue
                chat_id = upd["message"]["chat"]["id"]
                text = upd["message"].get("text")
                if not text:
                    continue
                process_message(chat_id, text)
                last_update_id = upd["update_id"]

        except requests.exceptions.ReadTimeout:
            # просто повторяем запрос при тайм-ауте
            continue
        except Exception as e:
            print("Ошибка при получении сообщений:", e)
            time.sleep(5)  # ждём 5 секунд перед повтором

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
