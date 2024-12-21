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

        # Check for left eye wink (landmark indices 159 and 145 for upper and lower eyelid)
        left_upper_lid = landmarks[159]
        left_lower_lid = landmarks[145]

        # Calculate the vertical distance between upper and lower eyelid for the left eye
        left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

        # Trigger a left click if the left eye distance is below the threshold
        if left_eye_dist < 0.01:
            
            pyautogui.click()
            pyautogui.sleep(.5)  # Pause to avoid multiple clicks

        # Check for right eye wink (landmark indices 386 and 374 for upper and lower eyelid)
        right_upper_lid = landmarks[386]
        right_lower_lid = landmarks[374]

        # Calculate the vertical distance between upper and lower eyelid for the right eye
        right_eye_dist = abs(right_upper_lid.y - right_lower_lid.y)

        # Trigger a right click if the right eye distance is below the threshold
        if right_eye_dist < 0.01:
            
            pyautogui.click(button='right')
            pyautogui.sleep(.5)  # Pause to avoid multiple clicks

    # Show the frame with the landmarks and the cursor position
    cv2.imshow('Nose Tip Controlled Mouse', frame)

    # Wait for a short time to control the speed of the loop
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release the camera and close the window
cam.release()
cv2.destroyAllWindows()
