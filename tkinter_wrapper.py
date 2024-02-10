# https://github.com/TomSchimansky/CustomTkinter
# https://customtkinter.tomschimansky.com/

from WhisperHandler import Whisper_Handler
import customtkinter
import os, json


class MyRadiobuttonFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)


class App(customtkinter.CTk):
    
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        self.title("Whisper App")
        self.geometry("400x240")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        with open("languages.json", 'r', encoding='utf-8') as file:
            whisper_languages = json.load(file)
            whisper_languages = {value: key for key, value in whisper_languages.items()}

        self.radiobutton_frame = MyRadiobuttonFrame(self, "Choose spoken language", values=whisper_languages)
        self.radiobutton_frame.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")

        chosen_language = self.radiobutton_frame.get()
        file_root = os.path.expanduser("~/Documents/Whisper/Data")
        # r"C:\Users\TThiele\Documents\Whisper\Data"
        wh = Whisper_Handler(file_root, chosen_language)

        button = customtkinter.CTkButton(master=self, text="Transcribe", command=self.button_callback)
        button.grid(row=2, column=0, padx=20, pady=20, sticky="ew", columnspan=2)


    def button_callback(self):
        print("button pressed")


app = App()
app.mainloop()