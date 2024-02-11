# === PACKAGE USED ===
# https://github.com/TomSchimansky/CustomTkinter
# https://customtkinter.tomschimansky.com/


import sys, os
root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_directory)
print(sys.path)
import customtkinter
import json
from model.WhisperHandler import Whisper_Handler
from utils.logging_custom import LogHandler
from datetime import datetime


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, logger=None, chosen_language=None, whisper_languages=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.lh = logger
        self.chosen_language = chosen_language
        self.whisper_languages = whisper_languages
        self.title("Running transcription")
        self.geometry("300x400")
        self.label = customtkinter.CTkLabel(self, text=f"Chosen language: {chosen_language}")
        self.label.pack(padx=20, pady=20)
        self.label = customtkinter.CTkLabel(self, text=f"Transcription is running ...")
        self.label.pack(padx=20, pady=20)
        self.after(3000, self.start_whisper_handler)

    def button_callback(self):
        self.lh.log("Top level window closed.")
        self.destroy()
        self.lh.log("Main window closed.")
        self.master.destroy()
    
    def start_whisper_handler(self):
        if self.chosen_language is not None:
            chosen_language_abbr = self.whisper_languages[self.chosen_language]
            file_root = os.path.expanduser("~/Documents/Whisper/Data")
            self.lh.log("Starting transcription with whisper.")
            wh = Whisper_Handler(file_root, chosen_language_abbr, logger=self.lh)
            state = wh.transcribe()
            
        self.label = customtkinter.CTkLabel(self, text=state)
        self.label.pack(padx=20, pady=20)

        button = customtkinter.CTkButton(master=self, text="Close", command=self.button_callback)
        button.pack(padx=20, pady=20)


class ScrollableRadiobuttonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        for i, value in enumerate(self.values):
            radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()
    def set(self, value):
        self.variable.set(value)


class App(customtkinter.CTk):
    
    def __init__(self, logger):
        super().__init__()
        
        self.lh = logger
        self.chosen_language = None
        self.toplevel_window = None

        # customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        # customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        self.title("Whisper App")
        self.geometry("300x400")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        with open("model/languages.json", 'r', encoding='utf-8') as file:
            whisper_languages = json.load(file)
            self.whisper_languages = {value: key for key, value in whisper_languages.items()}

        self.radiobutton_frame = ScrollableRadiobuttonFrame(self, "Choose spoken language", values=self.whisper_languages)
        self.radiobutton_frame.grid(row=0, column=0, padx=(0, 10), pady=(10, 0), sticky="w")

        button = customtkinter.CTkButton(master=self, text="Transcribe", command=self.button_callback)
        button.grid(row=2, column=0, padx=20, pady=20, sticky="ew", columnspan=2)      


    def button_callback(self):
        self.lh.log("Transcribe button pressed.")
        self.open_toplevel()


    def open_toplevel(self):
        chosen_language = self.radiobutton_frame.get()
        self.lh.log(f"Chosen language: {chosen_language}.")
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(
                self,
                logger=self.lh,
                chosen_language=chosen_language, 
                whisper_languages=self.whisper_languages
            )  # create window if its None or destroyed
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()  # if window exists focus it


if __name__ == "__main__":

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now()
    file_name = f"audio_transcription_{now.strftime('%Y_%m_%d-%H_%M_%S')}.txt"
    log_file_path = os.path.join(log_dir, file_name)

    lh = LogHandler(
        log_to_file=True,
        log_file_path=log_file_path
    )

    start = datetime.now()
    app = App(logger=lh)
    app.mainloop()
    end = datetime.now()
    duration = end - start
    duration_in_seconds = duration.total_seconds()
    lh.log(f"\n\nEND: Transcription app ran for {duration_in_seconds} seconds.")