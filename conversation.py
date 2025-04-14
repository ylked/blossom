import os
from openai import OpenAI
import sys

# silently import pygame
sys.stdout = open(os.devnull, 'w')
import pygame
# Reset standard output
sys.stdout = sys.__stdout__

CHAT_MODEL = "gpt-4o"
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "nova"
AUDIO_FILENAME = "speech.mp3"
PROMPT = "You are a social robot named Blossom used for education. "
PROMPT += "Your answers will be read out loud. "
PROMPT += "Keep them short and concise and adapted to children from 6 to 14 years old. "

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


def generate_audio(text):
    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
    )
    response.stream_to_file(AUDIO_FILENAME)


def play_audio():
    pygame.mixer.Sound(AUDIO_FILENAME).play()


def generate_answer(messages):
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages
    )
    return completion.choices[0].message.content


def run():
    def _append_content(content, role):
        messages.append({
            "role": role,
            "content": content
        })

    def append_user_question(question):
        _append_content(question, "user")

    def append_assistant_answer(answer):
        _append_content(answer, "assistant")

    messages = [
        {
            "role": "developer",
            "content": PROMPT
        }
    ]

    while True:
        question = input("You: ")
        append_user_question(question)
        answer = generate_answer(messages)
        append_assistant_answer(answer)
        generate_audio(answer)
        print(f"Blossom: {answer}")
        play_audio()


if __name__ == "__main__":
    pygame.mixer.init()
    run()
