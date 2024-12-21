import cv2
import mediapipe as mp
import pyautogui
import time
import speech_recognition as sr
import pyperclip
from pydub import AudioSegment
import spacy
from pydub.utils import which
from pynput.mouse import Listener
from pywinauto import Desktop

# Set up spaCy
nlp = spacy.load("en_core_web_sm")

AudioSegment.converter = which("ffmpeg")

# Initialize the recognizer
r = sr.Recognizer()

def remove_noise(audio_data):
    # ... (keep this function as it is)
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

def add_punctuation(text):
    # ... (keep this function as it is)
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

def replace_special_symbols(text):
    # ... (keep this function as it is)
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

    # Replace each specific trigger word with its corresponding symbol
    for keyword, symbol in symbol_map.items():
        text = text.replace(keyword, symbol)
    
    return text

def write_to_text_space(text):
    # ... (keep this function as it is)
    """Function to simulate typing the speech-to-text output into any active text field."""
    if text:
        pyautogui.write(text)  # Simulate typing the text in the active window


def copy_to_clipboard(text):
    # ... (keep this function as it is)
    """Function to copy the recognized text to the clipboard."""
    if text:
        pyperclip.copy(text)  # Copy the recognized text to clipboard
        print(f"Text copied to clipboard: {text}")

def real_time_recognition():
    # ... (keep this function as it is)
    """Function to continuously listen to the microphone and process speech."""
    with sr.Microphone() as source:
        print("Say something...")
        
        # Adjust the recognizer sensitivity to ambient noise (background noise)
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust sensitivity over 1 second

        while True:
            try:
                # Listen for audio input
                print("Listening...")
                audio = r.listen(source, timeout=3, phrase_time_limit=10)
                print("Processing...")

                # Apply noise reduction to the raw audio data
                processed_audio = remove_noise(audio.get_wav_data())

                # Create a new AudioData object from the processed raw data
                audio_file = sr.AudioData(processed_audio, source.SAMPLE_RATE, 2)

                # Convert speech to text using Google Web Speech API
                text = r.recognize_google(audio_file)

                # Add punctuation and grammar correction using spaCy
                punctuated_text = add_punctuation(text)

                # Replace special symbols based on specific triggers
                final_text = replace_special_symbols(punctuated_text)

                print(f"Processed text: {final_text}")

                # Write the recognized text into the active text field or application
                write_to_text_space(final_text)

                # Optionally, copy the recognized text to the clipboard
                copy_to_clipboard(final_text)

            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            
            except sr.RequestError:
                print("Sorry, I am having trouble with the speech service.")
                
            except Exception as e:
                print(f"An error occurred: {e}")


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

while True:
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

        # Check if the mouse is over a text box

        def is_mouse_over_editable_area():
            try:
                # Get the currently active window
                active_window = Desktop(backend="win32").active_window()

                if not active_window:
                    print("No active window detected")
                    return False

                # Get all text boxes (Edit controls) in the active window
                text_boxes = active_window.descendants(control_type="Edit")

                # Get the mouse position
                mouse_pos = pyautogui.position()

                # Check if the mouse is over any text box
                for text_box in text_boxes:
                    rect = text_box.rectangle()  # Bounding rectangle of the text box
                    if rect.left <= mouse_pos[0] <= rect.right and rect.top <= mouse_pos[1] <= rect.bottom:
                        return True

                return False
            except Exception as e:
                print(f"Error: {e}")
                return False

        # Prevent clicks when both eyes are closed
        if not (right_eye_dist < 0.008 and left_eye_dist < 0.008):
            if left_eye_dist < 0.008:
                if not left_eye_clicked:  # Prevent left click while mouse is down
                    if not mouse_down_flag:
                        pyautogui.click()  # Perform a left click, but not mouseDown
                        left_eye_clicked = True
                        real_time_recognition()
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
