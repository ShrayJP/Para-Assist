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
import spacy

capitalize_next=False

nlp = spacy.load("en_core_web_sm")

# Initialize the speech recognizer
r = sr.Recognizer()

class StartStopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Para-Assist")

        # Set window size and make it non-resizable
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Initialize a flag to track whether the app is "running"
        self.is_running = False

        # Set a modern background color for the window
        self.root.configure(bg="#f7f7f7")

        # Create a button frame to hold the close button
        self.top_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.top_frame.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        # Close button (styled)
        self.close_button = tk.Button(
            self.top_frame,
            text="Close",
            command=self.close_window,
            bg="#ff5c5c",  # Light red background for close button
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            width=8
        )
        self.close_button.pack()

        # Create a label for the app title
        self.title_label = tk.Label(
            self.root,
            text="Para-Assist",
            font=("Helvetica", 20, "bold"),
            fg="#333333",
            bg="#f7f7f7"
        )
        self.title_label.pack(pady=20)

        # Create a single Start/Stop button (styled)
        self.toggle_button = tk.Button(
            self.root,
            text="Start",
            command=self.toggle_action,
            width=15,
            height=2,
            bg="#4CAF50",  # Green background for start
            fg="white",
            font=("Helvetica", 14, "bold"),
            relief=tk.RAISED
        )
        self.toggle_button.pack(pady=40)

        # Start both face tracking and speech recognition immediately after launch
        self.toggle_action()
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
        # Sensitivity multiplier
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

        # Variables to store the previous position of the mouse and smoothed positions
        prev_screen_x, prev_screen_y = center_x, center_y
        smoothed_screen_x, smoothed_screen_y = center_x, center_y

        # Smoothing factor (higher values result in smoother movement)
        filter_alpha = 0.8

        # Variables for dragging feature
        dragging = False
        drag_start_x, drag_start_y = 0, 0
        eye_closed_start_time = 0
        eye_closed_threshold = 1  # Time in seconds to start dragging if the left eye is closed
        left_eye_clicked = False  # Flag to track if left click was already triggered
        mouse_down_flag = False  # Flag to prevent left click while mouse is down
        mouse_down_triggered = False  # Flag to prevent multiple mouseDown actions during dragging

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
                raw_screen_x = (nose_tip.x - 0.5) * screen_w  # Centered at (0, 0)
                raw_screen_y = (nose_tip.y - 0.5) * screen_h  # Centered at (0, 0)

                # Adjust sensitivity
                raw_screen_x = center_x + raw_screen_x * sensi_h
                raw_screen_y = center_y + raw_screen_y * sensi_v

                # Apply smoothing filter
                smoothed_screen_x = filter_alpha * smoothed_screen_x + (1 - filter_alpha) * raw_screen_x
                smoothed_screen_y = filter_alpha * smoothed_screen_y + (1 - filter_alpha) * raw_screen_y

                # Check for significant movement (to ignore small jitters)
                if abs(smoothed_screen_x - prev_screen_x) > 3 or abs(smoothed_screen_y - prev_screen_y) > 3:
                    if not dragging:
                        pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)
                    else:
                        # When dragging is enabled, move the mouse
                        pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)

                # Update the previous position
                prev_screen_x, prev_screen_y = smoothed_screen_x, smoothed_screen_y

                # Check for left eye wink (landmark indices 159 and 145 for upper and lower eyelid)
                left_upper_lid = landmarks[159]
                left_lower_lid = landmarks[145]

                # Calculate the vertical distance between upper and lower eyelid for the left eye
                left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

                # Check for right eye wink (landmark indices 386 and 374 for upper and lower eyelid)
                right_upper_lid = landmarks[386]
                right_lower_lid = landmarks[374]

                # Calculate the vertical distance between upper and lower eyelid for the right eye
                right_eye_dist = abs(right_upper_lid.y - right_lower_lid.y)

                # Prevent clicks when both eyes are closed
                if not (right_eye_dist < 0.008 and left_eye_dist < 0.008):
                    if left_eye_dist < 0.008:
                        if not left_eye_clicked:  # Prevent left click while mouse is down
                            # Trigger the left click immediately when the left eye is closed (only once)
                            if not mouse_down_flag :
                                pyautogui.click()  # Perform a left click, but not mouseDown
                                left_eye_clicked = True  # Mark that the click has been triggered
                                print("Left click triggered.")

                            # Sleep for 0.7 seconds before checking for drag
                            time.sleep(0.7)

                            # After the sleep, process the next frame and check eye distance again
                            _, frame = cam.read()
                            frame = cv2.flip(frame, 1)  # Flip frame horizontally
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            output = face_mesh.process(rgb_frame)
                            landmark_points = output.multi_face_landmarks
                            if landmark_points:
                                landmarks = landmark_points[0].landmark
                                left_upper_lid = landmarks[159]
                                left_lower_lid = landmarks[145]
                                left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

                            # Check if the left eye is still closed after the sleep
                            if left_eye_dist < 0.008:
                                # If the left eye is still closed, start dragging
                                dragging = True
                                drag_start_x, drag_start_y = smoothed_screen_x, smoothed_screen_y
                                if not mouse_down_triggered:
                                    pyautogui.mouseDown(smoothed_screen_x, smoothed_screen_y)  # Press the mouse down
                                    mouse_down_flag = True  # Set the flag to prevent left click while dragging
                                    mouse_down_triggered = True  # Set the flag to prevent multiple mouseDown actions
                                print("Mouse down triggered after 0.7 seconds.")

                    else:
                        # Only stop dragging and release mouse if the left eye is fully open
                        _, frame = cam.read()
                        frame = cv2.flip(frame, 1)  # Flip frame horizontally
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        output = face_mesh.process(rgb_frame)
                        landmark_points = output.multi_face_landmarks
                        if landmark_points:
                            landmarks = landmark_points[0].landmark
                            left_upper_lid = landmarks[159]
                            left_lower_lid = landmarks[145]
                            left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

                        if left_eye_dist > 0.008:
                            if dragging:
                                dragging = False  # Stop dragging when the left eye is open
                                pyautogui.mouseUp(smoothed_screen_x, smoothed_screen_y)  # Release the mouse button
                                print("Mouse released.")
                                pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)  # Ensure mouse stops moving
                                mouse_down_flag = False  # Reset the flag when the mouse is released
                                mouse_down_triggered = False  # Reset the flag to allow another mouse down

                        # Reset the left click flag when the left eye opens
                        left_eye_clicked = False

                    # Right click logic
                    if right_eye_dist < 0.008:
                        pyautogui.click(button='right')
                        print("Right click triggered.")
                        pyautogui.sleep(0.5)  # Pause to avoid multiple clicks

            # Show the frame with the landmarks and the cursor position
            cv2.imshow('Nose Tip Controlled Mouse', frame)

            # Wait for a short time to control the speed of the loop
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                break

        # Release the camera and close the window
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

    def delete_last_word():
        """Simulates deleting the last word typed."""
        # Use clipboard to retrieve current text in the active field
        pyautogui.hotkey("ctrl", "shift", "left")  # Select the last word
        pyautogui.press("backspace")

    def punctuation(self, text):
        """Use spaCy to add punctuation and structure to the recognized text."""
        doc = nlp(text)

        # Prepare a list to hold the punctuated sentences
        punctuated_text = []

        # Define question words
        question_words = {"who", "what", "how", "why", "where", "when", "do", "is", "are", "can", "couldn't", "wouldn't", "may"}

        # Iterate through sentences detected by spaCy
        for sent in doc.sents:
            sentence_text = sent.text.strip()

            # Check if the sentence seems like a question by examining the last word
            if sentence_text.lower().split()[0] in question_words:
                if not sentence_text.endswith('?'):
                    sentence_text += '?'  # Add question mark if not already there
            else:
                # Ensure it ends with a period if no question mark is detected
                if sentence_text and sentence_text[-1] not in [".", "?", "!"]:
                    sentence_text += "."

            sentence_text = sentence_text[0].upper() + sentence_text[1:]
            punctuated_text.append(sentence_text)

        # Combine sentences into a single string with spaces
        return " ".join(punctuated_text)

    def replace_special_symbols(self, text):
        """Replace predefined keywords with special symbols only in specified contexts."""
        symbol_map = {
            "symbol at": "@",
            "symbol hash": "#",
            "symbol dollar": "$",
            "symbol percent": "%",
            "symbol ampersand": "&",
            "symbol star": "*",
            "symbol plus": "+",
            "symbol minus": "-",
            "symbol equals": "=",
            "symbol underscore": "_",
            "symbol slash": "/",
            "symbol back": "\\",
            "symbol hyphen": "-"
        }

        
        action_map = {
            "press enter": "enter",
            "press delete": "backspace",
            "Press enter": "enter",
            "Press delete": "backspace"
        }

        global capitalize_next

        for keyword, action in action_map.items():
            if keyword in text.lower():
                if action == "backspace":
                    delete_last_word()
                elif action == "enter":
                    pyautogui.press(action)
                    capitalize_next=True

                # Remove the keyword from the text but preserve other parts of the input
                text = text.lower().replace(keyword, "").strip()

        # Replace special symbols
        for keyword, symbol in symbol_map.items():
            text = text.replace(keyword, symbol)

        return text

    def write_to_text_space(self, text):
        """Function to simulate typing the speech-to-text output into any active text field."""
        global capitalize_next
        if text:
            if capitalize_next:
                text = text[0].upper() + text[1:] if text else text
                capitalize_next = False  # Reset the flag after capitalizing
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

            while self.is_running:
                try:
                    print("Listening...")
                    # Listen for audio input
                    audio = r.listen(source, timeout=3, phrase_time_limit=10)
                    print("Processing...")

                    # Apply noise reduction to the raw audio data
                    processed_audio = self.remove_noise(audio.get_wav_data())

                    # Create a new AudioData object from the processed raw data
                    audio_file = sr.AudioData(processed_audio, source.SAMPLE_RATE, 2)

                    # Convert speech to text using Google Web Speech API
                    text = r.recognize_google(audio_file)

                    punctuated_text = self.punctuation(text)

                    final_text = self.replace_special_symbols(punctuated_text)

                    print(f"Processed text: {final_text}")

                    # Write the recognized text into the active text field or application
                    self.write_to_text_space(final_text)

                    # Optionally, copy the recognized text to the clipboard
                    self.copy_to_clipboard(final_text)

                except sr.UnknownValueError:
                    print("Sorry, I did not understand that.")

                except sr.RequestError:
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
