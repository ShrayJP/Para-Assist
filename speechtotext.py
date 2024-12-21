import speech_recognition as sr
import pyautogui
import pyperclip
from pydub import AudioSegment
import io
import time
from pydub.utils import which
import spacy

# Set up spaCy
nlp = spacy.load("en_core_web_sm")

AudioSegment.converter = which("ffmpeg")

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

def add_punctuation(text):
    """Use spaCy to add punctuation and structure to the recognized text."""
    doc = nlp(text)

    # Prepare a list to hold the punctuated sentences
    punctuated_text = []

    # Define question words
    question_words = {"who", "what", "how", "why", "where", "when", "do", "is", "are","can","couldn't","wouldn't","may"}

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

        while True:
            try:
                # Listen for audio input
                print("Listening...")
                audio = r.listen(source, timeout=3, phrase_time_limit=7)
                print("Processing...")

                # Apply noise reduction to the raw audio data
                processed_audio = remove_noise(audio.get_wav_data())

                # Create a new AudioData object from the processed raw data
                audio_file = sr.AudioData(processed_audio, source.SAMPLE_RATE, 2)

                # Convert speech to text using Google Web Speech API
                text = r.recognize_google(audio_file)

                # Add punctuation and grammar correction using spaCy
                punctuated_text = add_punctuation(text)
                print(f"Processed text: {punctuated_text}")

                # Write the recognized text into the active text field or application
                write_to_text_space(punctuated_text)

                # Optionally, copy the recognized text to the clipboard
                copy_to_clipboard(punctuated_text)

            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            
            except sr.RequestError:
                print("Sorry, I am having trouble with the speech service.")
                
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Start real-time recognition
    real_time_recognition()
