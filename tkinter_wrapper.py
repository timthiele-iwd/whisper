# https://github.com/TomSchimansky/CustomTkinter
# https://customtkinter.tomschimansky.com/

import customtkinter


class App(customtkinter.CTk):
    
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        self.title("Whisper App")
        self.geometry("400x240")

        self.grid_columnconfigure(0, weight=1)

        checkbox_1 = customtkinter.CTkCheckBox(self, text="German")
        checkbox_1.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        checkbox_2 = customtkinter.CTkCheckBox(self, text="English")
        checkbox_2.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="w")

        button = customtkinter.CTkButton(master=self, text="Transcribe audio", command=self.button_callback)
        button.grid(row=2, column=0, padx=20, pady=20, sticky="ew", columnspan=2)


    def button_callback(self):
        print("button pressed")


app = App()
app.mainloop()