import face_recognition
import os
import cv2
import pyttsx3
import numpy as np
import queue
import threading

cap = cv2.VideoCapture(0)

Face_IDs = "Face_IDs"
TOLERANCE = 0.4
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
# default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model
MODEL = "hog"


# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
    return color


def recognize_and_announce(frame, known_faces, known_names, q):
    locations = face_recognition.face_locations(frame)
    # print(locations)

    # Now since we know locations, we can pass them to face_encodings as second argument
    # Without that it will search for faces once again slowing down whole process
    encodings = face_recognition.face_encodings(frame, locations)

    # We passed our image through face_locations and face_encodings, so we can modify it
    # First we need to convert it from RGB to BGR as we are going to work with cv2
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
    # print(f', found {len(encodings)} face(s)')
    for face_encoding, face_location in zip(encodings, locations):

        # We use compare_faces (but might use face_distance as well)
        # Returns array of True/False values in order of passed known_faces
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

        # Since order is being preserved, we check if any face was found then grab index
        # then label (name) of first matching known face withing a tolerance
        match = None
        if (
            True in results
        ):  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            # print(f" - {match} from {results}")
            q.put(match)
            last = match
            print(match)
            print(results)
            # Each location contains positions in order: top, right, bottom, left
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])

            # Get color by name using our fancy function
            color = name_to_color(match)

            # Paint frame
            cv2.rectangle(frame, top_left, bottom_right, color, FRAME_THICKNESS)

            # Now we need smaller, filled grame below for a name
            # This time we use bottom in both corners - to start from bottom and move 50 pixels down
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2] + 22)

            # Paint frame
            cv2.rectangle(frame, top_left, bottom_right, color, cv2.FILLED)

            # Wite a name
            cv2.putText(
                frame,
                match,
                (face_location[3] + 10, face_location[2] + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                FONT_THICKNESS,
            )
        else:
            print(q.get())


# Function to speak names from the queue
def speak_from_queue(q, engine):
    while True:
        name = q.get()
        print(name)  # Wait for a name in the queue
        engine.say(name)
        engine.runAndWait()
        q.task_done()  # Signal task completion for queue management


print("Loading known faces...")
known_faces = []
known_names = []
print(Face_IDs)
# We organize known faces as subfolder of KNOWN_FACES_DIR
# Each subfolder's name becomes our label (name)
for name in os.listdir(Face_IDs):

    # Next we load every file of faces of known person
    for filename in os.listdir(f"{Face_IDs}/{name}"):

        # Load an image
        # image = face_recognition.load_image_file(f"{Face_IDs}/{name}/{filename}")
        image = cv2.imread(f"{Face_IDs}/{name}/{filename}")
        print(image.shape)
        # Get 128-dimension face encoding
        # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
        encoding = face_recognition.face_encodings(image)[0]

        # Append encodings and name
        known_faces.append(encoding)
        known_names.append(name)

print("Processing unknown faces...")
# Initialize the TTS engine
engine = pyttsx3.init()

# Create a queue for names
q = queue.Queue()

# Start the speech thread
speech_thread = threading.Thread(target=speak_from_queue, args=(q, engine))
speech_thread.daemon = True  # Set thread as daemon for graceful termination
speech_thread.start()
while True:
    ret, frame = cap.read()
    if ret is False:
        break
    recognize_and_announce(frame, known_faces, known_names, q)
    # Show image
    cv2.imshow("filename", frame)
    # cv2.namedWindow("filename", cv2.WINDOW_FREERATIO)
    if cv2.waitKey(1) == ord("q"):
        break
cv2.destroyAllWindows()
