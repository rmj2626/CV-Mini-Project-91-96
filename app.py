# from flask import Flask, render_template, request, jsonify, Response
# import cv2
# import mediapipe as mp
# import os
# from werkzeug.utils import secure_filename
# import time
# import math
# import threading

# class PoseDetector:
#     def __init__(self, mode=False, upBody=False, smooth=True,
#                  detectionCon=0.5, trackCon=0.5):
#         self.mode = mode
#         self.upBody = upBody
#         self.smooth = smooth
#         self.detectionCon = detectionCon
#         self.trackCon = trackCon

#         self.mpDraw = mp.solutions.drawing_utils
#         self.mpPose = mp.solutions.pose
#         self.pose = self.mpPose.Pose(static_image_mode=self.mode,
#                                     model_complexity=1,
#                                     smooth_landmarks=self.smooth,
#                                     min_detection_confidence=self.detectionCon,
#                                     min_tracking_confidence=self.trackCon)

#     def findPose(self, img, draw=True):
#         imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         self.results = self.pose.process(imgRGB)
#         if self.results.pose_landmarks:
#             if draw:
#                 self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
#                                          self.mpPose.POSE_CONNECTIONS)
#         return img

#     def findPosition(self, img, draw=True):
#         self.lmList = []
#         if self.results.pose_landmarks:
#             for id, lm in enumerate(self.results.pose_landmarks.landmark):
#                 h, w, c = img.shape
#                 cx, cy = int(lm.x * w), int(lm.y * h)
#                 self.lmList.append([id, cx, cy])
#                 if draw:
#                     cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
#         return self.lmList

#     def findAngle(self, img, p1, p2, p3, draw=True, exercise=None):
#         x1, y1 = self.lmList[p1][1:]
#         x2, y2 = self.lmList[p2][1:]
#         x3, y3 = self.lmList[p3][1:]

#         angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
#         if angle < 0:
#             angle += 360

#         if draw:
#             cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
#             cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
#             cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
#             cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
#             cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
#                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

#         feedback = ""
#         if exercise == "squat":
#             if angle < 90:
#                 feedback = "Go lower for squat"
#             elif angle > 100:
#                 feedback = "Too deep"
#             else:
#                 feedback = "Good form, continue!"
#         elif exercise == "pushup":
#             if angle < 230 or angle > 300:
#                 feedback = "Adjust push-up form"
#             else:
#                 feedback = "Good form, continue!"
#         elif exercise == "bicep_curl":
#             if angle < 30 or angle > 150:
#                 feedback = "Incorrect curl angle"
#             else:
#                 feedback = "Good form, continue!"
#         elif exercise == "plank":
#             if angle < 160:
#                 feedback = "Lower your hips"
#             elif angle > 200:
#                 feedback = "Raise your hips to align body"
#             else:
#                 feedback = "Good form, continue!"

#         if feedback:
#             cv2.putText(img, feedback, (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

#         return angle

# app = Flask(__name__)

# # Global variables for video processing
# global_frame = None
# processing_complete = threading.Event()
# current_video_path = None

# # Set upload folder and allowed extensions
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def process_video_frames(filepath, exercise_type="squat"):
#     global global_frame
#     cap = cv2.VideoCapture(filepath)
#     cap.set(3, 1280)
#     cap.set(4, 720)

#     detector = PoseDetector()
    
#     while not processing_complete.is_set():
#         success, img = cap.read()
#         if not success:
#             cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to beginning
#             continue

#         img = cv2.resize(img, (1280, 720))
#         img = detector.findPose(img)
#         lmList = detector.findPosition(img, draw=False)
        
#         if lmList:
#             if exercise_type == "squat":
#                 angle = detector.findAngle(img, 24, 26, 28, exercise="squat")
#             elif exercise_type == "pushup":
#                 angle = detector.findAngle(img, 11, 13, 15, exercise="pushup")
#             elif exercise_type == "plank":
#                 angle = detector.findAngle(img, 11, 23, 25, exercise="plank")
#             elif exercise_type == "bicep_curl":
#                 angle = detector.findAngle(img, 11, 13, 15, exercise="bicep_curl")

#         # # Calculate and display FPS
#         # cv2.putText(img, "Press 'q' to quit", (10, 30), 
#         #            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
#         # Convert frame to JPEG for streaming
#         ret, buffer = cv2.imencode('.jpg', img)
#         global_frame = buffer.tobytes()
        
#         time.sleep(0.03)  # Control frame rate

#     cap.release()

# def generate_frames():
#     while True:
#         if global_frame is not None:
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
#         time.sleep(0.03)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     global current_video_path
    
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     exercise_type = request.form.get('exercise_type', 'squat')

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if file and allowed_file(file.filename):
#         # Stop any existing video processing
#         processing_complete.set()
#         time.sleep(0.5)  # Give time for previous thread to close
#         processing_complete.clear()

#         # Save and process new video
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         if current_video_path and os.path.exists(current_video_path):
#             os.remove(current_video_path)  # Remove previous video
            
#         current_video_path = filepath

#         # Start processing in a new thread
#         thread = threading.Thread(target=process_video_frames, 
#                                 args=(filepath, exercise_type))
#         thread.daemon = True
#         thread.start()

#         return jsonify({"message": "Video processing started"})
#     else:
#         return jsonify({"error": "Invalid file type"}), 400

# @app.route('/stop_processing', methods=['POST'])
# def stop_processing():
#     processing_complete.set()
#     if current_video_path and os.path.exists(current_video_path):
#         os.remove(current_video_path)
#     return jsonify({"message": "Processing stopped"})

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify, Response
import cv2
import mediapipe as mp
import os
from werkzeug.utils import secure_filename
import time
import math
import threading

# Initialize Flask app
app = Flask(__name__)

# Global variables
global_frame = None
processing_complete = threading.Event()
current_video_path = None
current_feedback = ""  # Global variable for storing feedback

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper class for pose detection
class PoseDetector:
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode,
                                     model_complexity=1,
                                     smooth_landmarks=self.smooth,
                                     min_detection_confidence=self.detectionCon,
                                     min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, exercise=None):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        feedback = ""
        if exercise == "squat":
            if angle < 90:
                feedback = "Go lower for squat"
            elif angle > 100:
                feedback = "Too deep"
            else:
                feedback = "Good form, continue!"
        elif exercise == "pushup":
            if angle < 230 or angle > 300:
                feedback = "Adjust push-up form"
            else:
                feedback = "Good form, continue!"
        elif exercise == "bicep_curl":
            if angle < 30 or angle > 150:
                feedback = "Incorrect curl angle"
            else:
                feedback = "Good form, continue!"
        elif exercise == "plank":
            if angle < 160:
                feedback = "Lower your hips"
            elif angle > 200:
                feedback = "Raise your hips to align body"
            else:
                feedback = "Good form, continue!"

        return feedback

# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Process video frames and update feedback
def process_video_frames(filepath, exercise_type="squat"):
    global global_frame, current_feedback
    cap = cv2.VideoCapture(filepath)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = PoseDetector()
    
    while not processing_complete.is_set():
        success, img = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to beginning
            continue

        img = cv2.resize(img, (1280, 720))
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        
        if lmList:
            # Set feedback based on the exercise type and angle calculation
            if exercise_type == "squat":
                current_feedback = detector.findAngle(img, 24, 26, 28, exercise="squat")
            elif exercise_type == "pushup":
                current_feedback = detector.findAngle(img, 11, 13, 15, exercise="pushup")
            elif exercise_type == "plank":
                current_feedback = detector.findAngle(img, 11, 23, 25, exercise="plank")
            elif exercise_type == "bicep_curl":
                current_feedback = detector.findAngle(img, 11, 13, 15, exercise="bicep_curl")

        # Convert frame to JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', img)
        global_frame = buffer.tobytes()
        
        time.sleep(0.03)  # Control frame rate

    cap.release()

# Video feed generator
def generate_frames():
    while True:
        if global_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
        time.sleep(0.03)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_video_path
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    exercise_type = request.form.get('exercise_type', 'squat')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        processing_complete.set()
        time.sleep(0.5)
        processing_complete.clear()

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        if current_video_path and os.path.exists(current_video_path):
            os.remove(current_video_path)  # Remove previous video
            
        current_video_path = filepath

        # Start processing in a new thread
        thread = threading.Thread(target=process_video_frames, args=(filepath, exercise_type))
        thread.daemon = True
        thread.start()

        return jsonify({"message": "Video processing started"})
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/stop_processing', methods=['POST'])
def stop_processing():
    processing_complete.set()
    if current_video_path and os.path.exists(current_video_path):
        os.remove(current_video_path)
    return jsonify({"message": "Processing stopped"})

# Route to provide the current feedback
@app.route('/get_feedback')
def get_feedback():
    global current_feedback
    return jsonify({"feedback": current_feedback})

# Start the Flask app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
