import cv2
import pyttsx3
import queue
import threading


# Load your face recognition model (replace with your implementation)
def load_face_recognition_model():
    # Your code to load the face recognition model
    pass


# Function to recognize faces and add names to a queue for announcement
def recognize_and_announce(frame, q):
    # Face detection (replace with your implementation)
    name = "testing the code"
    q.put(name)


# Function to speak names from the queue
def speak_from_queue(q, engine):
    while True:
        name = q.get()  # Wait for a name in the queue
        engine.say(name)
        engine.runAndWait()
        q.task_done()  # Signal task completion for queue management


# Initialize the TTS engine
engine = pyttsx3.init()

# Video capture setup
cap = cv2.VideoCapture(0)  # Change 0 to video file path if needed

# Create a queue for names
q = queue.Queue()

# Start the speech thread
speech_thread = threading.Thread(target=speak_from_queue, args=(q, engine))
speech_thread.daemon = True  # Set thread as daemon for graceful termination
speech_thread.start()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Process the frame for face recognition
    recognize_and_announce(frame, q)

    # Display the resulting frame (optional)
    cv2.imshow("Face Recognition with Name Announcement", frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Wait for the queue to finish processing (optional)
# q.join()  # This waits for all queued names to be spoken

# Release capture resources
cap.release()
cv2.destroyAllWindows()

# Shut down the TTS engine
engine.shutdown()
