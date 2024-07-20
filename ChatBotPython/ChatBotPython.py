# library untuk GUI
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, messagebox
# library untuk membuka web, api, dan sejenisnya
import webbrowser
import requests
# library untuk handle latar belakang/background
import spacy
from PIL import Image, ImageTk
import cv2
import threading
# library untuk handle pertanyaan matematika
import os
import math
import re
# library untuk handle voice assist
from nltk.chat.util import Chat, reflections
import speech_recognition as sr
# library untuk handle delay, playsound, text to speech
import pygame
from io import BytesIO
import playsound
from gtts import gTTS

# load spacy model
nlp = spacy.load("en_core_web_sm")

# chat data >> still underconstructions
pairs = [
    [
        r"my name is (.*)",
        ["Hello %1, how can I assist you today?", "Hi %1! What can I do for you?"]
    ],
    [
        r"about you",
        ["I am an AI program created by my developer and named Fern AI. I'm here to help you!", 
         "I'm Fern AI, your helpful assistant created by wsnrfidev."]
    ],
    [
        r"can you help me?",
        ["Of course! What do you need help with?", 
         "Sure! Just let me know what you need assistance with.", 
         "Absolutely! I'm here to help you. What can I assist you with today?", 
         "Yes, I'm here to assist you. Please tell me how I can help."]
    ],
    [
        r"your information",
        ["Sure!\nVersion: Beta 0.0.1\nName: Fern AI\nDeveloper: wsnrfidev"]
    ],
    [
        r"hi|hello|hey",
        ["Hello! How can I assist you today?", "Hi there! What can I do for you?"]
    ],
    [
        r"whats your name?",
        ["You can call me Fern AI, your helpful virtual assistant.", 
         "I'm Fern AI, at your service!"]
    ],
    [
        r"how are you?",
        ["I'm just a program, so I don't have feelings, but I'm ready to help you!", 
         "I'm here and ready to assist you with anything you need."]
    ],
    [
        r"sorry (.*)",
        ["No worries!", "It's okay, I understand.", "No problem at all!"]
    ],
    [
        r"thank you|thanks",
        ["You're welcome!", "No problem!", "Glad I could help!", "Anytime!"]
    ],
    [
        r"bye|goodbye",
        ["Goodbye! Have a great day!", "See you later!", "Take care!", "Farewell!"]
    ],
    [
        r"open google",
        ["Sure, opening Google for you.", "Here's Google!", "Opening Google now."]
    ],
    [
        r"search google for (.*)",
        ["Sure, searching Google for %1.", "Let me look that up for you."]
    ],
    [
        r"open youtube",
        ["Sure, opening YouTube.", "Here's YouTube for you.", "Opening YouTube now."]
    ],
    [
        r"search youtube for (.*)",
        ["Sure, searching YouTube for %1.", "Looking that up on YouTube."]
    ],
    [
        r"open wikipedia",
        ["Sure, opening Wikipedia.", "Here's Wikipedia for you.", "Opening Wikipedia now."]
    ],
    [
        r"search wikipedia for (.*)",
        ["Sure, searching Wikipedia for %1.", "Let me find that on Wikipedia."]
    ],
    [
        r"open spotify",
        ["Sure, opening Spotify.", "Here's Spotify for you.", "Opening Spotify now."]
    ],
    [
        r"play (.*) on spotify",
        ["Sure, playing %1 on Spotify.", "Let me play %1 on Spotify for you."]
    ],
    [
        r"tell me a joke",
        ["Why don't scientists trust atoms? Because they make up everything!",
         "I used to play piano by ear, but now I use my hands like everyone else.",
         "I'm reading a book on anti-gravity. It's impossible to put down!"]
    ],
    [
        r"what can you do?",
        ["I can help you search the web, play music on Spotify, tell jokes, and answer general questions. Feel free to ask!", 
         "I can assist with searches, music, jokes, and answering questions. What do you need help with?"]
    ],
    [
        r"how can I help you?",
        ["You can help me by asking questions or requesting tasks like searching or playing music.", 
         "Just tell me what you need, and I'll do my best to assist!"]
    ],
    [
        r"what's up?",
        ["Not much, just here to assist you! How can I help today?", 
         "I'm here, ready to help with whatever you need!"]
    ],
    [
        r"(.*) favorite (.*)",
        ["I'm just a program, so I don't have personal favorites, but I'm here to assist with yours!", 
         "I don't have personal favorites, but I can help you find information on your favorites!"]
    ],
]

# membuat chatbot
chatbot = Chat(pairs, reflections)

# fungsi untuk voice assistant 
def speak(text):
    # fungsi untuk play audio dari objek file
    def play_audio(audio_file):
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # tunggu audio selesai diputar
            pygame.time.Clock().tick(10)

    # buat objek gtts untuk menghasilkan suara dari teks
    tts = gTTS(text=text, lang='en', slow=False)
    
    # simpan audio ke objek bytes io
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)

    def speak_thread():
        # putar audio di thread terpisah
        play_audio(audio_file)

    # jalankan pemutaran audio di thread terpisah untuk mengurangi delay antara chat dan suara
    thread = threading.Thread(target=speak_thread)
    thread.start()

# fungsi untuk mendengarkan dan menginisialisasi voice assistant
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""

# fungsi untuk mendapatkan entities
def get_entities(user_input):
    doc = nlp(user_input)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities

# fungsi untuk membuka URL
def open_url(url):
    webbrowser.open(url)

# fungsi untuk mendapatkan data dari wikipedia
def get_wikipedia_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('extract')
    else:
        return "I'm sorry, I couldn't find any information on that topic."

# fungsi untuk mendapatkan informasi cuaca di setiap daerah dan negara
def get_weather(city):
    api_key = "097eeb4580884927b8593469a739673f"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
    else:
        return "I'm sorry, I couldn't retrieve the weather data for that location."

# fungsi untuk handle pertanyaan matematika
def handle_math_question(question):
    patterns = [
        (r"do the math (\d+) plus (\d+)", "%d + %d"),
        (r"do the math (\d+) \+ (\d+)", "%d + %d"),
        (r"do the math (\d+) minus (\d+)", "%d - %d"),
        (r"do the math (\d+) - (\d+)", "%d - %d"),
        (r"do the math (\d+) times (\d+)", "%d * %d"),
        (r"do the math (\d+) \* (\d+)", "%d * %d"),
        (r"do the math (\d+) divided by (\d+)", "%d / %d"),
        (r"do the math (\d+) / (\d+)", "%d / %d"),
        (r"square root of (\d+)", "math.sqrt(%d)"),
        (r"cube root of (\d+)", "(%d) ** (1/3)"),
        (r"(\d+) factorial", "math.factorial(%d)")
    ]

    for pattern, operation in patterns:
        match = re.match(pattern, question)
        if match:
            operands = tuple(map(int, match.groups()))
            try:
                result = eval(operation % operands)
                return f"The result of {question} is {result}."
            except ZeroDivisionError:
                return "Error: Division by zero is undefined."
            except ValueError:
                return "Error: Invalid input for factorial operation."
    
    return None

# fungsi untuk memuat response dari chatbot
def chatbot_response(user_input):
    response = chatbot.respond(user_input)
    entities = get_entities(user_input)

    if "google" in user_input.lower():
        if "search" in user_input.lower():
            search_query = user_input.split("for ")[1]
            open_url(f"https://www.google.com/search?q={search_query}")
        else:
            open_url("https://www.google.com")
    elif "youtube" in user_input.lower():
        if "search" in user_input.lower():
            search_query = user_input.split("for ")[1]
            open_url(f"https://www.youtube.com/results?search_query={search_query}")
        else:
            open_url("https://www.youtube.com")
    elif "wikipedia" in user_input.lower():
        if "search" in user_input.lower():
            search_query = user_input.split("for ")[1]
            open_url(f"https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}")
        else:
            open_url("https://www.wikipedia.org")
    elif "spotify" in user_input.lower():
        if "play" in user_input.lower():
            search_query = user_input.split("play ")[1]
            open_url(f"https://open.spotify.com/search/{search_query}")
        else:
            open_url("https://open.spotify.com")
    elif "what is" in user_input.lower() or "who is" in user_input.lower() or "how to" in user_input.lower():
        search_query = user_input.split("is ")[1] if "is" in user_input.lower() else user_input.split("to ")[1]
        response = get_wikipedia_summary(search_query)
    elif "weather" in user_input.lower():
        city = user_input.split("in ")[1]
        response = get_weather(city)
    elif re.match(r"do the math|square root of|cube root of|(\d+) factorial|(\d+\s?(\+|\-|\*|\/|\^)\s?)+\d+", user_input):
        response = handle_math_question(user_input)
    return response, entities

# fungsi untuk mengirim pesan
def send_message():
    user_input = user_entry.get()
    user_message = "You: " + user_input + "\n\n"
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, user_message, 'user_message')
    chat_log.config(state=tk.DISABLED)
    user_entry.delete(0, tk.END)
    
    # Cek jika user menginput pertanyaan matematika
    math_response = handle_math_question(user_input)
    if math_response:
        bot_response = math_response
    else:
        # Handle jika bukan pertanyaan matematika
        if user_input.lower() in ['bye', 'goodbye']:
            bot_response = "Goodbye! Have a great day."
        else:
            bot_response, entities = chatbot_response(user_input)
            if entities:
                bot_response += "\n\nEntities: " + str(entities)
    
    # Memasukkan chatbot ke chat log
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Fern AI: " + bot_response + "\n\n", 'bot_message')
    chat_log.config(state=tk.DISABLED)
    
    # Scroll chat log
    chat_log.see(tk.END)

    # Memutar suara di thread terpisah
    speak(bot_response)
    
    # Scroll chat log
    chat_log.see(tk.END)

# fungsi untuk handle key press "ENTER" untuk mengirim pesan
def enter_pressed(event):
    send_message()

# fungsi untuk setup GUI
def setup_gui():
    global user_entry, chat_log

    root = tk.Tk()
    root.title("Fern AI Chatbot")
    root.geometry("800x500")

    # init video background/capture
    cap = cv2.VideoCapture('Assets/live_bg.mp4')
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open video file.")
        return

    canvas = tk.Canvas(root, width=1920, height=1080)
    canvas.pack()

    def update():
        nonlocal cap
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = ImageTk.PhotoImage(image=Image.fromarray(frame))
            canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            canvas.image = frame  # keep a reference
        else:
            cap.release()
            cap = cv2.VideoCapture('Assets/live_bg.mp4')
        canvas.after(30, update)

    update()

    chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, bg="#282c34", fg="white", insertbackground="white")
    chat_log.place(x=10, y=10, width=780, height=400)

    user_entry = Entry(root, width=80, bg="#1e1e1e", fg="#ffffff", insertbackground="white", font=("Helvetica", 12))
    user_entry.place(x=10, y=420, width=700, height=30)
    user_entry.bind("<Return>", enter_pressed)

    send_button_image = Image.open("Assets/send_button.png")
    send_button_image = send_button_image.resize((70, 30), Image.LANCZOS)
    send_button_photo = ImageTk.PhotoImage(send_button_image)
    send_button = tk.Button(root, image=send_button_photo, borderwidth=0, command=send_message)
    send_button.image = send_button_photo
    send_button.place(x=720, y=420, width=70, height=30)

    chat_log.tag_configure('user_message', justify='right', foreground='white')
    chat_log.tag_configure('bot_message', justify='left', foreground='white')

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Fern AI: Hello! I am Fern AI. Type 'bye' or 'goodbye' to exit.\n\nHow can I assist you today?\n\n", 'bot_message')
    chat_log.config(state=tk.DISABLED)

    # tambahkan button untuk voice input
    voice_button = tk.Button(root, text="🎤", command=voice_input_thread)
    voice_button.place(x=10, y=460, width=70, height=30)

    root.mainloop()


# fungsi untuk input dari voice assistant
def voice_input_thread():
    thread = threading.Thread(target=voice_input)
    thread.start()

# fungsi voice input
def voice_input():
    user_input = listen()
    if user_input:
        user_message = "You: " + user_input + "\n\n"
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, user_message, 'user_message')
        chat_log.config(state=tk.DISABLED)

        bot_response, entities = chatbot_response(user_input)
        if entities:
            bot_response += "\n\nEntities: " + str(entities)

        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "Fern AI: " + bot_response + "\n\n", 'bot_message')
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)

        # Memutar suara di thread terpisah
        speak(bot_response)
        
# jalankan setup GUI
setup_gui()
