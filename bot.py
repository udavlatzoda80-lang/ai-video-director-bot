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


def make_project(topic):

    scenes = [
        ("HOOK", "Start with a surprising question about " + topic),
        ("ORIGIN", "Show the earliest human situation connected to the topic"),
        ("PROBLEM", "Explain the problem humans needed to solve"),
        ("EARLY SOLUTION", "Show the first simple solution"),
        ("CHANGE", "Show how the idea started changing society"),
        ("EXPANSION", "Show how the idea spread between communities"),
        ("IMPORTANT MOMENT", "Show a major historical turning point"),
        ("PEOPLE", "Show ordinary people experiencing the change"),
        ("CONFLICT", "Show problems and conflicts created by the change"),
        ("INNOVATION", "Show an important innovation"),
        ("SYSTEM", "Explain how the system became organized"),
        ("WORLD", "Show how different civilizations used the idea"),
        ("MODERNIZATION", "Show the transition toward the modern world"),
        ("BIG CHANGE", "Show the biggest transformation"),
        ("TODAY", "Connect the historical story to modern life"),
        ("SURPRISE", "Reveal an interesting lesser-known fact"),
        ("LESSON", "Explain what this history teaches us"),
        ("ENDING", "Finish with a memorable question or conclusion")
    ]

    result = []

    result.append(
        "🎬 AI VIDEO DIRECTOR — 10 MINUTE PROJECT\n\n"
        f"📌 TOPIC:\n{topic}\n\n"
        "⏱ TARGET LENGTH: 8–10 minutes\n"
        "🎨 STYLE: Animated History / Documentary\n"
        "🌎 AUDIENCE: US + Europe\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📝 VIDEO STRUCTURE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )

    result.append(
        "🎙️ OPENING / HOOK\n\n"
        f"Imagine a world before {topic.lower()} existed.\n"
        "How did humans go from simple survival to the system we know today?\n"
        "This is the story of how it happened.\n\n"
    )

    result.append(
        "🎬 SCENES\n\n"
    )

    for i, (name, description) in enumerate(scenes, 1):

        visual = (
            f"Animated historical documentary scene, {description.lower()}, "
            "cinematic composition, expressive cartoon characters, "
            "historically inspired environment, detailed background, "
            "dramatic lighting, educational animation, 16:9"
        )

        result.append(
            f"SCENE {i:02d} — {name}\n"
            f"🎙 VOICEOVER:\n"
            f"{description} related to {topic}.\n\n"
            f"🖼 VISUAL PROMPT:\n{visual}\n\n"
            f"🎥 CAMERA:\nSlow cinematic movement, documentary style.\n\n"
        )

    result.append(
        "━━━━━━━━━━━━━━━━━━\n"
        "🎵 AUDIO\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Background music: cinematic historical documentary.\n"
        "Use subtle sound effects between important scenes.\n"
        "Keep voice clearly louder than music.\n\n"
    )

    result.append(
        "━━━━━━━━━━━━━━━━━━\n"
        "🖼 THUMBNAIL\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Create a highly clickable animated history thumbnail about {topic}. "
        "One strong central character, dramatic historical background, "
        "large readable English text, cinematic lighting, 16:9.\n\n"
    )

    result.append(
        "━━━━━━━━━━━━━━━━━━\n"
        "📺 YOUTUBE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"TITLE:\nHow Did Humans Invent {topic.replace('How Did Humans Invent ', '')}?\n\n"
        "DESCRIPTION:\n"
        f"Discover the fascinating history behind {topic}. "
        "From the earliest human societies to the modern world.\n\n"
        "#History #Animation #Documentary #HumanHistory"
    )

    return "".join(result)


def handle_update(update):

    message = update.get("message")

    if not message:
        return

    user = message.get("from", {})
    user_id = user.get("id")
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if user_id != OWNER_ID:
        send_message(chat_id, "⛔ Access denied.")
        return

    if text == "/start":

        send_message(
            chat_id,
            "🎬 AI VIDEO DIRECTOR v2\n\n"
            "Салом!\n\n"
            "Менга видео мавзусини юборинг.\n\n"
            "Масалан:\n"
            "How Did Humans Invent Money?\n\n"
            "Мен сизга:\n"
            "📝 Script structure\n"
            "🎬 18 Scenes\n"
            "🖼 Visual prompts\n"
            "🎙 Voiceover plan\n"
            "🎵 Audio plan\n"
            "🖼 Thumbnail prompt\n"
            "📺 YouTube title + description\n\n"
            "тайёрлайман."
        )

        return

    if text:

        send_message(
            chat_id,
            "🎬 Мавзу қабул қилинди!\n\n"
            f"📌 {text}\n\n"
            "⏳ Director ишлаяпти..."
        )

        project = make_project(text)

        # Telegram message limit protection
        chunk_size = 3500

        for i in range(0, len(project), chunk_size):

            send_message(
                chat_id,
                project[i:i + chunk_size]
            )

            time.sleep(1)


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

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()

        self.wfile.write(
            b"AI Video Director v2 is running!"
        )

    def log_message(self, format, *args):
        return


def start_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


if __name__ == "__main__":

    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    print(
        "AI Video Director v2 started!"
    )

    polling()
