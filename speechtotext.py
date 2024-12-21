import speech_recognition as sr
import pyautogui
import pyperclip
import time

# Initialize the recognizer
r = sr.Recognizer()

def write_to_text_space(text):
    """Function to simulate typing the speech-to-text output into any active text field."""
    if text:
        pyautogui.write(text)  # Simulate typing the text in the active window

def copy_to_clipboard(text):
    """Function to copy the recognized text to the clipboard."""
    if text:
        pyperclip.copy(text)  # Copy the recognized text to clipboard
        print(f"Text copied to clipboard: {text}")

def real_time_recognition():
    """Function to continuously listen to the microphone and process speech."""
    with sr.Microphone() as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise

        # Use a context manager to listen continuously without breaking
        while True:
            try:
                # Listen for speech
                print("Listening...")
                audio = r.listen(source, timeout=3, phrase_time_limit=5)  # Adjust timeout & phrase_time_limit
                print("Processing...")

                # Convert speech to text using Google Web Speech API
                text = r.recognize_google(audio)
                print(f"You said: {text}")
                
                # Write the recognized text into the active text field or application
                write_to_text_space(text)
                
                # Optionally, copy the recognized text to the clipboard
                copy_to_clipboard(text)

            except sr.UnknownValueError:
                # Error: speech was unintelligible
                print("Sorry, I did not understand that.")
            
            except sr.RequestError:
                # Error: API request failed
                print("Sorry, I am having trouble with the speech service.")
                
            except Exception as e:
                # General error handling to avoid crashes
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Start real-time recognition
    real_time_recognition()
