import speech_recognition as sr
import pyttsx3
import pyautogui
import time

# Initialize the recognizer and text-to-speech engine
r = sr.Recognizer()
engine = pyttsx3.init()

def output_text(text):
    """Function to convert text to speech and output ihello what are you sayingyou are not gayt."""
    if text:
        print(f"Outputting text: {text}")
        engine.say(text)  # Convert text to speech
        engine.runAndWait()  # Run the speech engine

def write_to_text_space(text):
    """Function to simulate typing the speech-to-text output into any active text field."""
    if text:
        pyautogui.write(text)  # Simulate typing the text in the active window
    

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
                audio = r.listen(source, timeout=2, phrase_time_limit=5)  # Adjust timeout & phrase_time_limit
                print("Processing...")

                # Convert speech to text using Google Web Speech API
                text = r.recognize_google(audio)
                print(f"You said: {text}")
                
                # Output text using text-to-speech
                output_text(text)
                
                # Write the recognized text into the active text field or application
                write_to_text_space(text)

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
