import asyncio
import threading
import os
import edge_tts
import pygame
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import itertools
import datetime
import webbrowser

DEFAULT_VOICE = "en-AU-WilliamNeural"
HISTORY_FILE = "history/spoken_texts.txt"
os.makedirs("history", exist_ok=True)


def remove_file(file_path):
    """Safely remove a file if exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass


async def amain(text, output_file, voice):
    """Generate TTS using edge-tts and play it"""
    try:
        cm_txt = edge_tts.Communicate(text, voice)
        await cm_txt.save(output_file)
        threading.Thread(target=play_audio, args=(
            output_file,), daemon=True).start()
    except Exception as e:
        print(f"TTS Error: {e}")


def play_audio(file_path):
    """Play the generated audio using pygame"""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16,
                              channels=2, buffer=4096)

        sound = pygame.mixer.Sound(file_path)
        sound.play()

        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(5)

        remove_file(file_path)
    except Exception as e:
        print(f"Audio Error: {e}")


def speak(text, voice=DEFAULT_VOICE, output_file=None):
    """Generate and play TTS instantly with thread-safe asyncio loop"""
    if output_file is None:
        output_file = f"{os.getcwd()}/speech.mp3"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(amain(text, output_file, voice))
        loop.close()
    except Exception as e:
        print(f"Speak Error: {e}")
    finally:
        log_history(text)


def log_history(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")


root = tk.Tk()
root.title("🎙️EchoJarvis --- Speak Freely.. Hear Instantly..! 🎙️")
root.geometry("777x777+10+10")
root.config(bg="#121212")
root.overrideredirect(True)
root.resizable(False, False)

try:
    import ctypes
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, 2, ctypes.byref(ctypes.c_int(1)), 4)
except:
    pass

titlebar = tk.Frame(root, bg="#0D0D0D", relief="raised", bd=0, height=35)
titlebar.pack(fill=tk.X, side=tk.TOP)

app_title = tk.Label(
    titlebar,
    text="🎙️EchoJarvis  —  Speak Freely.. Hear Instantly..!  🎙️",
    bg="#0D0D0D",
    fg="#00FFB3",
    font=("Poppins", 12, "bold"),
)
app_title.pack(side=tk.LEFT, padx=10)


def minimize_window():
    root.iconify()


def toggle_maximize():
    if root.state() == "zoomed":
        root.state("normal")
    else:
        root.state("zoomed")


def close_window():
    root.destroy()


btn_close = tk.Button(titlebar, text="✖", bg="#0D0D0D", fg="#FF4B4B",
                      border=0, font=("Arial", 12, "bold"), command=close_window)
btn_max = tk.Button(titlebar, text="⬜", bg="#0D0D0D", fg="#00E0FF",
                    border=0, font=("Arial", 12, "bold"), command=toggle_maximize)
btn_min = tk.Button(titlebar, text="➖", bg="#0D0D0D", fg="#00FFB3",
                    border=0, font=("Arial", 12, "bold"), command=minimize_window)

btn_close.pack(side=tk.RIGHT, padx=8, pady=3)
btn_max.pack(side=tk.RIGHT, padx=8, pady=3)
btn_min.pack(side=tk.RIGHT, padx=8, pady=3)


def start_move(event):
    root.x = event.x
    root.y = event.y


def stop_move(event):
    root.x = None
    root.y = None


def on_motion(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")


titlebar.bind("<Button-1>", start_move)
titlebar.bind("<ButtonRelease-1>", stop_move)
titlebar.bind("<B1-Motion>", on_motion)

colors = ["#121212", "#1E1E1E", "#00FFB3", "#0078FF", "#FF0078", "#FFAA00"]
color_cycle = itertools.cycle(colors)


def animate_bg():
    new_color = next(color_cycle)
    root.config(bg=new_color)
    title_label.config(bg=new_color)
    tagline_label.config(bg=new_color)
    text_box.config(bg=new_color)
    root.after(2000, animate_bg)


title_label = tk.Label(root, text="🎙️EchoJarvis ", font=(
    "Poppins", 28, "bold"), fg="#00FFB3", bg="#121212")
title_label.pack(pady=(20, 5))

tagline_label = tk.Label(root, text="💬 Speak Freely.. Hear Instantly..!", font=(
    "Poppins", 14, "italic"), fg="#CCCCCC", bg="#121212")
tagline_label.pack(pady=(0, 20))

tk.Label(root, text="Enter Text to Speak:", fg="white",
         bg="#121212", font=("Segoe UI", 12)).pack()
text_entry = tk.Entry(root, width=65, font=("Segoe UI", 12))
text_entry.pack(pady=5)

tk.Label(root, text="Select Voice:", fg="white",
         bg="#121212", font=("Segoe UI", 12)).pack()
voice_options = [
    "en-AU-WilliamNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-GB-RyanNeural"
]
voice_select = ttk.Combobox(root, values=voice_options, font=("Segoe UI", 12))
voice_select.current(0)
voice_select.pack(pady=5)


def speak_from_entry():
    text = text_entry.get().strip()
    if text:
        threading.Thread(target=lambda: speak(
            text, voice_select.get()), daemon=True).start()
        text_box.config(state=tk.NORMAL)
        text_box.insert(tk.END, f"You: {text}\n")
        text_box.see(tk.END)
        text_box.config(state=tk.DISABLED)


def preview_voice(v):
    threading.Thread(target=lambda: speak(
        "This is a preview of the selected voice.", v), daemon=True).start()


btn_frame = tk.Frame(root, bg="#121212")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🎙️ Speak", command=speak_from_entry, bg="#00FFB3", fg="black",
          font=("Segoe UI", 12, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="📜 Show History", command=lambda: show_history(), bg="#0078FF",
          fg="white", font=("Segoe UI", 12, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="🎧 Preview Voice", command=lambda: preview_voice(voice_select.get()),
          bg="#FFAA00", fg="black", font=("Segoe UI", 12, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)

text_box = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, height=15, width=85, bg="#1E1E1E", fg="#00FFB3", font=("Consolas", 11))
text_box.pack(padx=10, pady=10)
text_box.config(state=tk.DISABLED)


def show_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_window = tk.Toplevel(root)
            history_window.title("📜 Speech History")
            history_window.geometry("500x400")
            history_text = scrolledtext.ScrolledText(
                history_window, wrap=tk.WORD)
            history_text.insert(tk.END, f.read())
            history_text.config(state=tk.DISABLED)
            history_text.pack(fill=tk.BOTH, expand=True)
    except FileNotFoundError:
        messagebox.showinfo("Info", "No history found yet!")


footer_frame = tk.Frame(root, bg="#121212")
footer_frame.pack(side=tk.BOTTOM, pady=10)

footer_label = tk.Label(footer_frame, text="👨‍💻 Rama Lingeswara Rao Sivakavi | 🔊 Powered by Python",
                        fg="#888888", bg="#121212", font=("Segoe UI", 10))
footer_label.pack()


def open_pygame_link(event):
    webbrowser.open_new("https://www.pygame.org/contribute.html")


link_label = tk.Label(footer_frame, text="🔗 Contribute to Pygame",
                      fg="#00AAFF", bg="#121212", font=("Segoe UI", 10, "underline"), cursor="hand2")
link_label.pack()
link_label.bind("<Button-1>", open_pygame_link)

animate_bg()
root.mainloop()
