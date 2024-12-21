import cv2
import mediapipe as mp
import pyautogui
import time

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

# Variables to store the previous position of the mouse and smoothed positions
prev_screen_x, prev_screen_y = center_x, center_y
smoothed_screen_x, smoothed_screen_y = center_x, center_y

# Smoothing factor (higher values result in smoother movement)
filter_alpha = 0.8

# Variables for dragging feature
dragging = False
drag_start_x, drag_start_y = 0, 0
eye_closed_start_time = 0
eye_closed_threshold = 1  # Time in seconds to start dragging if the left eye is closed
left_eye_clicked = False  # Flag to track if left click was already triggered
mouse_down_flag = False  # Flag to prevent left click while mouse is down
mouse_down_triggered = False  # Flag to prevent multiple mouseDown actions during dragging

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
        raw_screen_x = (nose_tip.x - 0.5) * screen_w  # Centered at (0, 0)
        raw_screen_y = (nose_tip.y - 0.5) * screen_h  # Centered at (0, 0)

        # Adjust sensitivity
        raw_screen_x = center_x + raw_screen_x * sensi_h
        raw_screen_y = center_y + raw_screen_y * sensi_v

        # Apply smoothing filter
        smoothed_screen_x = filter_alpha * smoothed_screen_x + (1 - filter_alpha) * raw_screen_x
        smoothed_screen_y = filter_alpha * smoothed_screen_y + (1 - filter_alpha) * raw_screen_y

        # Check for significant movement (to ignore small jitters)
        if abs(smoothed_screen_x - prev_screen_x) > 3 or abs(smoothed_screen_y - prev_screen_y) > 3:
            if not dragging:
                pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)
            else:
                # When dragging is enabled, move the mouse
                pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)

        # Update the previous position
        prev_screen_x, prev_screen_y = smoothed_screen_x, smoothed_screen_y

        # Check for left eye wink (landmark indices 159 and 145 for upper and lower eyelid)
        left_upper_lid = landmarks[159]
        left_lower_lid = landmarks[145]

        # Calculate the vertical distance between upper and lower eyelid for the left eye
        left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

        # Check for right eye wink (landmark indices 386 and 374 for upper and lower eyelid)
        right_upper_lid = landmarks[386]
        right_lower_lid = landmarks[374]

        # Calculate the vertical distance between upper and lower eyelid for the right eye
        right_eye_dist = abs(right_upper_lid.y - right_lower_lid.y)

        # Prevent clicks when both eyes are closed
        if not (right_eye_dist < 0.008 and left_eye_dist < 0.008):
            if left_eye_dist < 0.008:
                if not left_eye_clicked:  # Prevent left click while mouse is down
                    # Trigger the left click immediately when the left eye is closed (only once)
                    if not mouse_down_flag :
                        pyautogui.click()  # Perform a left click, but not mouseDown
                        left_eye_clicked = True  # Mark that the click has been triggered
                        print("Left click triggered.")

                    # Sleep for 0.7 seconds before checking for drag
                    time.sleep(0.7)

                    # After the sleep, process the next frame and check eye distance again
                    _, frame = cam.read()
                    frame = cv2.flip(frame, 1)  # Flip frame horizontally
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    output = face_mesh.process(rgb_frame)
                    landmark_points = output.multi_face_landmarks
                    if landmark_points:
                        landmarks = landmark_points[0].landmark
                        left_upper_lid = landmarks[159]
                        left_lower_lid = landmarks[145]
                        left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)

                    # Check if the left eye is still closed after the sleep
                    if left_eye_dist < 0.008:
                        # If the left eye is still closed, start dragging
                        dragging = True
                        drag_start_x, drag_start_y = smoothed_screen_x, smoothed_screen_y
                        if not mouse_down_triggered:
                            pyautogui.mouseDown(smoothed_screen_x, smoothed_screen_y)  # Press the mouse down
                            mouse_down_flag = True  # Set the flag to prevent left click while dragging
                            mouse_down_triggered = True  # Set the flag to prevent multiple mouseDown actions
                        print("Mouse down triggered after 0.7 seconds.")

            else:
                # Only stop dragging and release mouse if the left eye is fully open
                _, frame = cam.read()
                frame = cv2.flip(frame, 1)  # Flip frame horizontally
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output = face_mesh.process(rgb_frame)
                landmark_points = output.multi_face_landmarks
                if landmark_points:
                    landmarks = landmark_points[0].landmark
                    left_upper_lid = landmarks[159]
                    left_lower_lid = landmarks[145]
                    left_eye_dist = abs(left_upper_lid.y - left_lower_lid.y)
                
                if left_eye_dist > 0.008:
                    if dragging:
                        dragging = False  # Stop dragging when the left eye is open
                        pyautogui.mouseUp(smoothed_screen_x, smoothed_screen_y)  # Release the mouse button
                        print("Mouse released.")
                        pyautogui.moveTo(smoothed_screen_x, smoothed_screen_y)  # Ensure mouse stops moving
                        mouse_down_flag = False  # Reset the flag when the mouse is released
                        mouse_down_triggered = False  # Reset the flag to allow another mouse down

                # Reset the left click flag when the left eye opens
                left_eye_clicked = False

            # Right click logic
            if right_eye_dist < 0.008:
                pyautogui.click(button='right')
                print("Right click triggered.")
                pyautogui.sleep(0.5)  # Pause to avoid multiple clicks

    # Show the frame with the landmarks and the cursor position
    cv2.imshow('Nose Tip Controlled Mouse', frame)

    # Wait for a short time to control the speed of the loop
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release the camera and close the window
cam.release()
cv2.destroyAllWindows()
