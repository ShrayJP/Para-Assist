import speech_recognition as sr
import pyautogui
import pyperclip
from pydub import AudioSegment
import io
import time

# Initialize the recognizer
r = sr.Recognizer()

def remove_noise(audio_data):
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
        
        # Adjust the recognizer sensitivity to ambient noise (background noise)
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust sensitivity over 1 second

        print("Listening...")
        while True:
            try:
                # Listen for audio input
                audio = r.listen(source, timeout=3, phrase_time_limit=5)
                print("Processing...")

                # Apply noise reduction to the raw audio data
                processed_audio = remove_noise(audio.get_wav_data())

                # Create a new AudioData object from the processed raw data
                audio_file = sr.AudioData(processed_audio, source.SAMPLE_RATE, 2)

                # Convert speech to text using Google Web Speech API
                text = r.recognize_google(audio_file)
                print(f"You said: {text}")

                # Write the recognized text into the active text field or application
                write_to_text_space(text)

                # Optionally, copy the recognized text to the clipboard
                copy_to_clipboard(text)

            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            
            except sr.RequestError:
                print("Sorry, I am having trouble with the speech service.")
                
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Start real-time recognition
    real_time_recognition()
