import os
import json
import time
import threading
import asyncio
import textwrap
import tempfile

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFont

import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


# =========================
# SETTINGS
# =========================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 7258495769

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# TELEGRAM API
# =========================

def telegram(method, data=None, files=None):
    data = data or {}

    if files:
        import requests

        response = requests.post(
            f"{API}/{method}",
            data=data,
            files=files,
            timeout=180
        )

        return response.json()

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


def send_video(chat_id, video_path):

    with open(video_path, "rb") as video_file:

        telegram(
            "sendVideo",
            {
                "chat_id": chat_id,
                "caption": "🎬 Your AI video is ready!"
            },
            {
                "video": video_file
            }
        )


# =========================
# PROJECT GENERATOR
# =========================

def make_project(topic):

    scenes = [
        ("HOOK",
         f"Imagine a world before {topic} existed."),

        ("ORIGIN",
         f"Let's go back to the earliest history connected with {topic}."),

        ("PROBLEM",
         f"People faced an important problem that eventually led to {topic}."),

        ("EARLY SOLUTION",
         f"Early humans created simple solutions connected with {topic}."),

        ("CHANGE",
         f"The idea of {topic} slowly began changing human society."),

        ("EXPANSION",
         f"The concept spread between different communities."),

        ("IMPORTANT MOMENT",
         f"A major historical moment changed the development of {topic}."),

        ("PEOPLE",
         f"Ordinary people experienced these changes in everyday life."),

        ("CONFLICT",
         f"The development also created new problems and conflicts."),

        ("INNOVATION",
         f"New inventions helped improve the way {topic} was used."),

        ("SYSTEM",
         f"Eventually, societies created organized systems around the idea."),

        ("WORLD",
         f"Different civilizations developed their own versions."),

        ("MODERNIZATION",
         f"The idea continued changing as the modern world developed."),

        ("BIG CHANGE",
         f"One of the biggest transformations completely changed {topic}."),

        ("TODAY",
         f"Today, {topic} remains connected to everyday life."),

        ("SURPRISE",
         f"There is also a surprising fact about the history of {topic}."),

        ("LESSON",
         f"The history of {topic} can teach us something about human society."),

        ("ENDING",
         f"So what will the future of {topic} look like?")
    ]

    project = []

    project.append(
        f"""
🎬 AI VIDEO DIRECTOR

📌 TOPIC:
{topic}

⏱ TARGET LENGTH:
8–10 minutes

🎨 STYLE:
Animated Historical Documentary

🌎 AUDIENCE:
US + Europe

━━━━━━━━━━━━━━━━━━
🎙 SCRIPT
━━━━━━━━━━━━━━━━━━

"""
    )

    for number, (name, voiceover) in enumerate(scenes, 1):

        visual = (
            f"Animated historical documentary scene about {topic}, "
            f"{voiceover}, cinematic composition, "
            f"expressive characters, detailed historical environment, "
            f"dramatic lighting, educational animation, 16:9"
        )

        project.append(
            f"""
SCENE {number:02d} — {name}

🎙 VOICEOVER:
{voiceover}

🖼 VISUAL:
{visual}

🎥 CAMERA:
Slow cinematic documentary movement.

━━━━━━━━━━━━━━━━━━
"""
        )

    project.append(
        f"""
🎵 AUDIO

Cinematic historical documentary music.
Voice should be louder than background music.

━━━━━━━━━━━━━━━━━━

🖼 THUMBNAIL

Clickable YouTube thumbnail about {topic},
dramatic historical background,
one strong central character,
large readable English title,
cinematic lighting, 16:9.

━━━━━━━━━━━━━━━━━━

📺 YOUTUBE TITLE

The History of {topic}

📄 DESCRIPTION

Discover the fascinating history of {topic},
from its earliest beginnings to the modern world.

#History #Animation #Documentary #HumanHistory
"""
    )

    return "".join(project)


# =========================
# EXTRACT SCENES
# =========================

def create_scenes(topic):

    scenes = [
        (
            "HOOK",
            f"Imagine a world before {topic} existed."
        ),
        (
            "ORIGIN",
            f"Let's go back to the earliest history connected with {topic}."
        ),
        (
            "PROBLEM",
            f"People faced an important problem that eventually led to {topic}."
        ),
        (
            "EARLY SOLUTION",
            f"Early humans created simple solutions connected with {topic}."
        ),
        (
            "CHANGE",
            f"The idea of {topic} slowly began changing human society."
        ),
        (
            "EXPANSION",
            f"The concept spread between different communities."
        ),
        (
            "IMPORTANT MOMENT",
            f"A major historical moment changed the development of {topic}."
        ),
        (
            "PEOPLE",
            f"Ordinary people experienced these changes in everyday life."
        ),
        (
            "CONFLICT",
            f"The development also created new problems and conflicts."
        ),
        (
            "INNOVATION",
            f"New inventions helped improve the way {topic} was used."
        ),
        (
            "SYSTEM",
            f"Eventually, societies created organized systems around the idea."
        ),
        (
            "WORLD",
            f"Different civilizations developed their own versions."
        ),
        (
            "MODERNIZATION",
            f"The idea continued changing as the modern world developed."
        ),
        (
            "BIG CHANGE",
            f"One of the biggest transformations completely changed {topic}."
        ),
        (
            "TODAY",
            f"Today, {topic} remains connected to everyday life."
        ),
        (
            "SURPRISE",
            f"There is also a surprising fact about the history of {topic}."
        ),
        (
            "LESSON",
            f"The history of {topic} can teach us something about human society."
        ),
        (
            "ENDING",
            f"So what will the future of {topic} look like?"
        )
    ]

    return scenes


# =========================
# FONT
# =========================

def get_font(size):

    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    for font in possible_fonts:

        if os.path.exists(font):
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()


# =========================
# CREATE SCENE IMAGE
# =========================

def create_scene_image(topic, scene_name, text, path):

    width = 1280
    height = 720

    image = Image.new(
        "RGB",
        (width, height),
        (18, 18, 25)
    )

    draw = ImageDraw.Draw(image)

    title_font = get_font(52)
    text_font = get_font(34)
    small_font = get_font(24)

    # simple cinematic background

    for y in range(height):

        value = int(
            18 +
            (y / height) * 25
        )

        draw.line(
            [(0, y), (width, y)],
            fill=(value, value, value + 8)
        )

    # title

    draw.text(
        (70, 70),
        scene_name,
        font=title_font,
        fill="white"
    )

    # topic

    draw.text(
        (70, 145),
        topic[:70],
        font=small_font,
        fill="gray"
    )

    # wrapped voiceover

    wrapped = textwrap.fill(
        text,
        width=48
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=text_font,
        spacing=15
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    draw.multiline_text(
        (x, y),
        wrapped,
        font=text_font,
        fill="white",
        spacing=15,
        align="center"
    )

    draw.text(
        (70, 665),
        "AI VIDEO DIRECTOR",
        font=small_font,
        fill="gray"
    )

    image.save(path)


# =========================
# TEXT TO SPEECH
# =========================

async def generate_voice(text, output):

    communicate = edge_tts.Communicate(
        text,
        "en-US-GuyNeural"
    )

    await communicate.save(output)


def make_voice(text, output):

    asyncio.run(
        generate_voice(
            text,
            output
        )
    )


# =========================
# VIDEO GENERATOR
# =========================

def generate_video(topic):

    temp_dir = tempfile.mkdtemp(
        prefix="ai_video_"
    )

    scenes = create_scenes(topic)

    clips = []

    for index, (name, voice_text) in enumerate(
        scenes,
        1
    ):

        image_path = os.path.join(
            temp_dir,
            f"scene_{index}.jpg"
        )

        audio_path = os.path.join(
            temp_dir,
            f"scene_{index}.mp3"
        )

        create_scene_image(
            topic,
            name,
            voice_text,
            image_path
        )

        make_voice(
            voice_text,
            audio_path
        )

        audio = AudioFileClip(
            audio_path
        )

        clip = ImageClip(
            image_path
        ).with_duration(
            audio.duration
        ).with_audio(
            audio
        )

        clips.append(clip)

    final_video = concatenate_videoclips(
        clips,
        method="compose"
    )

    output_path = os.path.join(
        temp_dir,
        "final_video.mp4"
    )

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium"
    )

    final_video.close()

    for clip in clips:

        try:
            clip.close()
        except:
            pass

    return output_path


# =========================
# TELEGRAM HANDLER
# =========================

def handle_update(update):

    message = update.get("message")

    if not message:
        return

    user = message.get(
        "from",
        {}
    )

    user_id = user.get("id")

    chat_id = message["chat"]["id"]

    text = message.get(
        "text",
        ""
    ).strip()

    # security

    if user_id != OWNER_ID:

        send_message(
            chat_id,
            "⛔ Access denied."
        )

        return

    # START

    if text == "/start":

        send_message(
            chat_id,

            "🎬 AI VIDEO DIRECTOR v3\n\n"

            "Салом!\n\n"

            "Менга видео мавзусини юборинг.\n\n"

            "Масалан:\n"
            "How Did Humans Invent Money?\n\n"

            "Мен:\n"
            "📝 Script\n"
            "🎬 18 Scenes\n"
            "🎙 Voiceover\n"
            "🎥 MP4 Video\n"
            "📺 YouTube title\n\n"

            "тайёрлайман.\n\n"

            "Аввал мавзу юборинг."
        )

        return

    # VIDEO COMMAND

    if text.upper() == "VIDEO":

        send_message(
            chat_id,
            "❗ Аввал мавзу юборинг.\n\n"
            "Масалан:\n"
            "How Did Humans Invent Money?"
        )

        return

    # TOPIC

    if text:

        send_message(
            chat_id,

            "🎬 Мавзу қабул қилинди!\n\n"
            f"📌 {text}\n\n"
            "📝 Сценарий тайёрланяпти..."
        )

        project = make_project(text)

        chunk_size = 3500

        for i in range(
            0,
            len(project),
            chunk_size
        ):

            send_message(
                chat_id,
                project[i:i + chunk_size]
            )

            time.sleep(1)

        send_message(
            chat_id,

            "━━━━━━━━━━━━━━━━━━\n"
            "🎥 VIDEO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "Видео тайёрлашни бошлаш учун:\n\n"

            "VIDEO\n\n"

            "деб ёзинг."
        )

        # save topic

        with open(
            "last_topic.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        return


# =========================
# POLLING
# =========================

def polling():

    offset = None

    while True:

        try:

            data = {
                "timeout": 30
            }

            if offset is not None:
                data["offset"] = offset

            result = telegram(
                "getUpdates",
                data
            )

            if result.get("ok"):

                for update in result.get(
                    "result",
                    []
                ):

                    offset = (
                        update["update_id"] + 1
                    )

                    # VIDEO command processing

                    message = update.get(
                        "message"
                    )

                    if message:

                        text = message.get(
                            "text",
                            ""
                        ).strip()

                        chat_id = message[
                            "chat"
                        ]["id"]

                        user_id = message.get(
                            "from",
                            {}
                        ).get(
                            "id"
                        )

                        if (
                            user_id == OWNER_ID
                            and text.upper()
                            == "VIDEO"
                        ):

                            if not os.path.exists(
                                "last_topic.txt"
                            ):

                                send_message(
                                    chat_id,
                                    "❗ Аввал мавзу юборинг."
                                )

                                continue

                            with open(
                                "last_topic.txt",
                                "r",
                                encoding="utf-8"
                            ) as f:

                                topic = f.read().strip()

                            send_message(
                                chat_id,
                                "🎬 VIDEO GENERATOR\n\n"
                                f"📌 {topic}\n\n"
                                "⏳ Видео тайёрланяпти...\n"
                                "Бу бироз вақт олиши мумкин."
                            )

                            try:

                                video_path = generate_video(
                                    topic
                                )

                                send_video(
                                    chat_id,
                                    video_path
                                )

                                send_message(
                                    chat_id,
                                    "✅ Видео тайёр!\n\n"
                                    "🎬 MP4 форматда."
                                )

                            except Exception as e:

                                print(
                                    "VIDEO ERROR:",
                                    e
                                )

                                send_message(
                                    chat_id,
                                    "❌ Видео тайёрлашда хато чиқди.\n\n"
                                    f"{str(e)[:1000]}"
                                )

                            continue

                    handle_update(
                        update
                    )

        except Exception as e:

            print(
                "Polling error:",
                e
            )

            time.sleep(5)


# =========================
# HEALTH SERVER
# =========================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()

        self.wfile.write(
            b"AI Video Director v3 is running!"
        )

    def log_message(
        self,
        format,
        *args
    ):
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


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    print(
        "AI Video Director v3 started!"
    )

    polling()
