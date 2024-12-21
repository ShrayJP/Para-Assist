import tkinter as tk

# Define the StartStopApp class
class StartStopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Para-Assist")

        # Set window size and background color to black
        self.root.geometry("600x500")
        self.root.configure(bg='black')  # Change background color to black

        # Create a frame for the header (title) at the top
        self.header_frame = tk.Frame(self.root, bg='black')
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        # Add a title label (header) for Para-Assist
        self.header_label = tk.Label(self.header_frame, text="Para-Assist", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.header_label.pack(pady=10)

        # Create a frame for the buttons (right side)
        self.button_frame = tk.Frame(self.root, bg='black')
        self.button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Create a single Start/Stop button with rounded corners and white border
        self.toggle_button = tk.Button(self.button_frame, text="Start", width=20, height=2, bg='black', fg='white', command=self.toggle, relief="solid", borderwidth=5, highlightthickness=2, highlightbackground="white", highlightcolor="white", padx=10, pady=10)
        self.toggle_button.pack(pady=10)

        # Create a Close button with rounded corners, white border, and black background
        self.close_button = tk.Button(self.button_frame, text="Close", command=self.close_window, width=20, height=2, bg='black', fg='white', relief="solid", borderwidth=5, highlightthickness=2, highlightbackground="white", highlightcolor="white", padx=10, pady=10)
        self.close_button.pack()

        # Add a documentation heading label above the text box
        self.doc_heading_label = tk.Label(self.root, text="Documentation", font=("Arial", 18, "bold"), fg="white", bg="black")
        self.doc_heading_label.pack(side=tk.TOP, pady=(20, 5))  # Padding top and bottom of the label

        # Create a frame for the text box (left side)
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y, expand=True)

        # Create a Text widget with a vertical scrollbar
        self.text_box = tk.Text(self.text_frame, width=40, height=15, wrap=tk.WORD, bg='black', fg='white')
        self.text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a vertical scrollbar for the text box
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Link the scrollbar to the text box
        self.text_box.config(yscrollcommand=self.scrollbar.set)

        # Bind the event for resizing the window
        self.root.bind("<Configure>", self.on_resize)

    def toggle(self):
        """Toggle the button text between 'Start' and 'Stop'."""
        if self.toggle_button['text'] == "Start":
            self.toggle_button.config(text="Stop")
        else:
            self.toggle_button.config(text="Start")

    def close_window(self):
        """Close the application."""
        self.root.quit()

    def on_resize(self, event):
        """Handle window resizing."""
        if event.width == self.root.winfo_screenwidth() and event.height == self.root.winfo_screenheight():
            # If the window is full-screen, increase button size
            self.toggle_button.config(width=30, height=4)
            self.close_button.config(width=30, height=4)
        else:
            # If the window is not full-screen, restore original button size
            self.toggle_button.config(width=20, height=2)
            self.close_button.config(width=20, height=2)

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the StartStopApp
    app = StartStopApp(root)

    # Run the Tkinter main loop
    root.mainloop()
