"""
Audio Handler Module
Handles microphone input and speech recognition
"""

import speech_recognition as sr
import threading
import time
from queue import Queue


class AudioHandler:
    def __init__(self):
        """Initialize the audio handler with speech recognition"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.audio_queue = Queue()
        self.listen_thread = None
        self.current_transcript = ""
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Ready to listen!")
    
    def start_listening(self):
        """Start listening for speech in a separate thread"""
        if not self.is_listening:
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            return True
        return False
    
    def stop_listening(self):
        """Stop the listening thread"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        return True
    
    def _listen_loop(self):
        """Main listening loop running in background thread"""
        with self.microphone as source:
            while self.is_listening:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Process audio in a separate thread to not block
                    threading.Thread(target=self._process_audio, args=(audio,)).start()
                    
                except sr.WaitTimeoutError:
                    # Timeout occurred, continue listening
                    continue
                except Exception as e:
                    print(f"Error during listening: {e}")
                    time.sleep(0.1)
    
    def _process_audio(self, audio):
        """Process the captured audio and convert to text"""
        try:
            # Recognize speech using Google Web Speech API
            text = self.recognizer.recognize_google(audio)
            if text:
                self.current_transcript = text
                self.audio_queue.put(text)
                print(f"Recognized: {text}")
        except sr.UnknownValueError:
            # Could not understand audio
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def get_latest_text(self):
        """Get the latest transcribed text from the queue"""
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None
    
    def get_all_texts(self):
        """Get all pending transcribed texts"""
        texts = []
        while not self.audio_queue.empty():
            texts.append(self.audio_queue.get())
        return texts
    
    def set_energy_threshold(self, threshold):
        """Adjust the energy threshold for voice detection"""
        self.recognizer.energy_threshold = threshold
    
    def set_pause_threshold(self, threshold):
        """Adjust the pause threshold for phrase detection"""
        self.recognizer.pause_threshold = threshold
