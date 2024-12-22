import customtkinter as ctk
import tkinter as tk
ctk.set_appearance_mode("System")  # Use the system appearance mode (light/dark)
ctk.set_default_color_theme("blue")  # Set the default color theme to blue

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hack For Tomorrow")
        
        #image=ctk.CtkImage(file="1734823780393.png")
       # label=ctk.CTkLabel(app,image=image,text="")
       # label.pack(pady=20)
        # Set window size and center the window on the screen
        self.root.geometry("400x500")
        self.root.eval('tk::PlaceWindow . center')  # Center the window

        # Set window resizeable (make sure elements scale well)
        self.root.grid_rowconfigure(0, weight=0)  # Heading row is fixed size
        self.root.grid_rowconfigure(1, weight=1)  # Description section expands
        self.root.grid_rowconfigure(2, weight=0)  # Button row is fixed size
        self.root.grid_columnconfigure(0, weight=1)  # Single column expands

        # Heading (title)
        self.heading_label = ctk.CTkLabel(self.root, text="Para-Assist", font=("Helvetica", 34, "bold"), text_color="white")
        self.heading_label.grid(row=0, column=0, pady=80, padx=20, sticky="nsew")  # Center the heading label
        
        # Scrollable description frame
        self.text_frame = ctk.CTkFrame(self.root)
        self.text_frame.grid(row=1, column=0, pady=20, padx=20, sticky="nsew")  # Fill space and expand
        
        # Create and configure the scrollbar (left side)
        self.scrollbar = ctk.CTkScrollbar(self.text_frame, orientation="vertical")
        self.scrollbar.grid(row=0, column=0, sticky="ns", padx=(10, 10),pady=(10,10))  # Scrollbar is placed on the left

        # Create and configure the text widget (right side of the scrollbar)
        self.text_widget = ctk.CTkTextbox(self.text_frame, wrap="word", yscrollcommand=self.scrollbar.set, font=("Arial", 12))
        self.text_widget.insert("0.0", """This system allows hands-free computer interaction using eye gestures and voice commands. It includes features like eye movement-based mouse control, voice-to-text input, and easy insertion of special symbols through voice commands.
        
Features:
Eye Navigation (Mouse Control)

Left Wink (Left Click): Wink your left eye to simulate a left mouse click.
Right Wink (Right Click): Wink your right eye to simulate a right mouse click.
Left Wink Hold (Drag & Scroll): Hold a left wink to drag and select items or scroll down the page.
Voice to Text

Voice Typing: Speak normally, and the system will convert your speech into text for any text input area.
Special Symbols via Voice

Say "symbol [name]": For inserting special characters, say "symbol [symbol name]" (e.g., “symbol dollar” for $ or “symbol at” for @).
Libraries to Use:
numpy

Install: pip install numpy
Description: Supports arrays and mathematical operations.
opencv-python

Install: pip install opencv-python
Description: Computer vision library for image/video processing.
pyautogui

Install: pip install pyautogui
Description: Automates mouse and keyboard control.
mediapipe

Install: pip install mediapipe
Description: ML pipelines for face/hand tracking and other tasks.
speechrecognition

Install: pip install SpeechRecognition
Description: Converts speech to text.
pyaudio

Install: pip install pyaudio
Description: Handles audio input/output.
pyttsx3

Install: pip install pyttsx3
Description: Converts text to speech (offline).""")
        self.text_widget.grid(row=0, column=1, sticky="nsew")  # Text widget takes remaining space in grid
        self.scrollbar.configure(command=self.text_widget.yview)  # Link the scrollbar with the text widget
        
        # Start/Stop button with fixed size (100x80)
        self.button = ctk.CTkButton(self.root, text="Start", command=self.toggle_button, font=("Helvetica", 22), width=300, height=80, corner_radius=40)
        self.button.grid(row=2, column=0, pady=20, padx=20)  # The button is fixed size, no need for sticky or expansion

        # Bind the window resizing event to update the height of the text frame
        self.root.bind("<Configure>", self.update_scrollable_area)

    def toggle_button(self):
        current_text = self.button.cget("text")
        if current_text == "Start":
            self.button.configure(text="Stop")  # Change color on toggle
        else:
            self.button.configure(text="Start")  # Reset color

    def update_scrollable_area(self, event):
        # Get the current height and width of the window
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Adjust the height of the text frame and text widget
        self.text_frame.configure(height=window_height - 140)  # Leave space for heading and button
        self.text_widget.configure(height=window_height - 140)  # Adjust height dynamically with window size
        self.text_widget.configure(width=window_width - 200)  # Adjust width dynamically with window size (subtracting space for scrollbar)

if __name__ == "__main__":
    app = ctk.CTk()  # create window
    app.geometry("400x500")  # set the size of the window
    modern_app = ModernApp(app)
    app.mainloop()
