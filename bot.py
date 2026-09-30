import os
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.parse import urlencode

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 7258495769

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def telegram(method, data=None):
    data = data or {}
    body = urlencode(data).encode()

    req = Request(
        f"{API}/{method}",
        data=body,
        method="POST"
    )

    with urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode())


def send_message(chat_id, text):
    telegram(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text
        }
    )


def handle_update(update):
    message = update.get("message")

    if not message:
        return

    user = message.get("from", {})
    user_id = user.get("id")
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # Only owner can use the bot
    if user_id != OWNER_ID:
        send_message(
            chat_id,
            "⛔ Access denied."
        )
        return

    if text == "/start":
        send_message(
            chat_id,
            "🎬 AI VIDEO DIRECTOR\n\n"
            "Салом! Мен сизнинг AI Video Director ботингизман.\n\n"
            "Менга видео мавзусини юборинг.\n\n"
            "Масалан:\n"
            "How Did Humans Invent Money?\n\n"
            "Мен мавзуни 10 дақиқалик видео лойиҳасига айлантираман."
        )
        return

    if text:
        send_message(
            chat_id,
            "🎬 Мавзу қабул қилинди!\n\n"
            f"📌 Topic:\n{text}\n\n"
            "⏳ Лойиҳа тайёрланмоқда...\n\n"
            "1️⃣ Research\n"
            "2️⃣ Script\n"
            "3️⃣ Scenes\n"
            "4️⃣ Visuals\n"
            "5️⃣ Voice\n"
            "6️⃣ Editing\n\n"
            "🚧 Ҳозирча бу биринчи тест версия."
        )


def polling():
    offset = None

    while True:
        try:
            data = {
                "timeout": 30
            }

            if offset is not None:
                data["offset"] = offset

            result = telegram("getUpdates", data)

            if result.get("ok"):
                for update in result.get("result", []):
                    offset = update["update_id"] + 1
                    handle_update(update)

        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AI Video Director Bot is running!")

    def log_message(self, format, *args):
        return


def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    print("AI Video Director Bot started!")
    polling()
