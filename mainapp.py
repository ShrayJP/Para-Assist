import tkinter as tk
from tkinter import messagebox
import cv2
import mediapipe as mp
import pyautogui
import threading
import speech_recognition as sr
import pyperclip
from pydub import AudioSegment
import time

# Sensitivity multiplier for face tracking
sensi_h = 5
sensi_v = 11
# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False

# Initialize camera and MediaPipe Face Mesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get screen resolution
screen_w, screen_h = pyautogui.size()

# Find the center of the screen
center_x, center_y = screen_w // 2, screen_h // 2

# Initialize the speech recognizer
r = sr.Recognizer()

class StartStopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Para-Assist")
        
        # Initialize a flag to track whether the app is "running"
        self.is_running = False

        # Set window size (You can change the size as per your need)
        self.root.geometry("400x300")

        # Create a single Start/Stop button
        self.toggle_button = tk.Button(self.root, text="Start", command=self.toggle_action, width=15, height=2)
        self.toggle_button.pack(pady=100)

        # Create a button frame to hold the close button
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        # Close button (will be handled by Tkinter)
        self.close_button = tk.Button(self.top_frame, text="Close", command=self.close_window, width=10)
        self.close_button.pack(side=tk.RIGHT)

    def toggle_action(self):
        """Handles the start/stop button functionality."""
        if not self.is_running:
            self.is_running = True
            self.toggle_button.config(text="Stop")  # Change button text to "Stop"
            
            # Start both the face tracking and speech recognition in separate threads
            threading.Thread(target=self.start_face_tracking, daemon=True).start()
            threading.Thread(target=self.real_time_recognition, daemon=True).start()

        else:
            self.is_running = False
            self.toggle_button.config(text="Start")  # Change button text back to "Start"

    def start_face_tracking(self):
        """This function will run the face-tracking and mouse control in a loop."""
        while self.is_running:
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)  # Flip frame horizontally
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe
            output = face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w, _ = frame.shape

            if landmark_points:
                landmarks = landmark_points[0].landmark

                # Use the landmark corresponding to the nose tip (landmark 1)
                nose_tip = landmarks[1]  # Nose tip landmark index is 1
                x = int(nose_tip.x * frame_w)
                y = int(nose_tip.y * frame_h)

                # Draw the nose tip on the frame for visualization
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

                # Translate the coordinates relative to the center of the screen
                screen_x = (nose_tip.x - 0.5) * screen_w  # Centered at (0, 0)
                screen_y = (nose_tip.y - 0.5) * screen_h  # Centered at (0, 0)

                # Move the mouse to the new position (adjust sensitivity)
                pyautogui.moveTo(center_x + screen_x * sensi_h, center_y + screen_y * sensi_v)

                # Check for left eye wink (landmark indices 159 and 145 for upper and lower eyelid)
                left_upper_lid = landmarks[159]
                left_lower_lid = landmarks[145]

                # Calculate the vertical distance between upper and lower eyelid for the left eye
                left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

                # Trigger a left click if the left eye distance is below the threshold
                if left_eye_dist < 0.01:
                    pyautogui.click()
                    pyautogui.sleep(0.5)  # Pause to avoid multiple clicks

                # Check for right eye wink (landmark indices 386 and 374 for upper and lower eyelid)
                right_upper_lid = landmarks[386]
                right_lower_lid = landmarks[374]

                # Calculate the vertical distance between upper and lower eyelid for the right eye
                right_eye_dist = abs(right_upper_lid.y - right_lower_lid.y)

                # Trigger a right click if the right eye distance is below the threshold
                if right_eye_dist < 0.01:
                    pyautogui.click(button='right')
                    pyautogui.sleep(0.5)  # Pause to avoid multiple clicks

            # Show the frame with the landmarks and the cursor position
            cv2.imshow('Nose Tip Controlled Mouse', frame)

            # Wait for a short time to control the speed of the loop
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                break

        # Release the camera and close the window once stopped
        cam.release()
        cv2.destroyAllWindows()

    def remove_noise(self, audio_data):
        """Apply basic noise reduction using pydub."""
        # Convert raw audio to an AudioSegment for noise reduction
        audio_segment = AudioSegment(
            audio_data,
            frame_rate=16000,  # Match the microphone's sample rate
            channels=1,
            sample_width=2
        )

        # Apply a simple noise reduction by reducing background volume (placeholder for more advanced methods)
        audio_segment = audio_segment - 10  # Reduce background noise by 10dB

        # Return the processed audio as raw data
        return audio_segment.raw_data

    def write_to_text_space(self, text):
        """Function to simulate typing the speech-to-text output into any active text field."""
        if text:
            pyautogui.write(text)  # Simulate typing the text in the active window

    def copy_to_clipboard(self, text):
        """Function to copy the recognized text to the clipboard."""
        if text:
            pyperclip.copy(text)  # Copy the recognized text to clipboard
            print(f"Text copied to clipboard: {text}")

    def real_time_recognition(self):
        """Function to continuously listen to the microphone and process speech."""
        with sr.Microphone() as source:
            print("Say something...")

            # Adjust the recognizer sensitivity to ambient noise (background noise)
            r.adjust_for_ambient_noise(source, duration=1)  # Adjust sensitivity over 1 second

            print("Listening...")
            while self.is_running:
                try:
                    # Listen for audio input
                    audio = r.listen(source, timeout=3, phrase_time_limit=5)
                    print("Processing...")

                    # Apply noise reduction to the raw audio data
                    processed_audio = self.remove_noise(audio.get_wav_data())

                    # Create a new AudioData object from the processed raw data
                    audio_file = sr.AudioData(processed_audio, source.SAMPLE_RATE, 2)

                    # Convert speech to text using Google Web Speech API
                    text = r.recognize_google(audio_file)
                    print(f"You said: {text}")

                    # Write the recognized text into the active text field or application
                    self.write_to_text_space(text)

                    # Optionally, copy the recognized text to the clipboard
                    self.copy_to_clipboard(text)

                except sr.UnknownValueError:
                    print("Sorry, I did not understand that.")

                except sr.RequestError:monkey near
                    print("Sorry, I am having trouble with the speech service.")

                except Exception as e:
                    print(f"An error occurred: {e}")

    def close_window(self):
        """Close the application and stop the background tasks."""
        self.is_running = False
        self.root.quit()


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the StartStopApp
    app = StartStopApp(root)

    # Run the main loop
    root.mainloop()
