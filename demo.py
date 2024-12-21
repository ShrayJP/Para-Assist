import cv2
import mediapipe as mp
import pyautogui

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
        screen_x = (nose_tip.x - 0.5) * screen_w  # Centered at (0, 0)
        screen_y = (nose_tip.y - 0.5) * screen_h  # Centered at (0, 0)

        # Move the mouse to the new position (adjust sensitivity)
        pyautogui.moveTo(center_x + screen_x * sensi_h, center_y + screen_y * sensi_v)
        print(f"Cursor position: {screen_x}, {screen_y}")

    # Show the frame with the landmarks and the cursor position
    cv2.imshow('Nose Tip Controlled Mouse', frame)

    # Wait for a short time to control the speed of the loop
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release the camera and close the window
cam.release()
cv2.destroyAllWindows()
