import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Set the text you want to convert to speech
text = "This is some text to be spoken by pyTTSx3."

# Set the speaking rate (optional)
engine.setProperty("rate", 150)  # Adjust the rate as desired (default is 150)

# Set the volume (optional)
engine.setProperty("volume", 1.0)  # Adjust the volume from 0.0 to 1.0 (default is 1.0)

# Say the text
engine.say(text)

# Wait for the speech to finish
engine.runAndWait()
