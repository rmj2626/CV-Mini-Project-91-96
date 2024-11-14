import cv2
import time
import PoseModule as pm

# Set up video capture and resolution
cap = cv2.VideoCapture('PoseVideos/plank.mp4')
cap.set(3, 1280)  # Set width to 1280 for 720p
cap.set(4, 720)   # Set height to 720 for 720p

pTime = 0
detector = pm.poseDetector()

while True:
    success, img = cap.read()
    if not success:
        break

    # Resize the frame to ensure consistent 720p output
    img = cv2.resize(img, (1280, 720))
    
    # Detect pose and provide feedback
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)
    if lmList:
        angle_knee = detector.findAngle(img, 24, 26, 28, exercise="plank")  # Example for squat

    # Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Display the video
    cv2.imshow("Exercise Feedback", img)

    # Exit if 'q' is pressed or window is closed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Close if the window is clicked outside
    if cv2.getWindowProperty("Exercise Feedback", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
