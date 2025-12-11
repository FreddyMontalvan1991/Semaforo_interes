import cv2
import mediapipe as mp
import numpy as np
from math import hypot

mp_face_mesh = mp.solutions.face_mesh

RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE  = [362, 385, 387, 263, 373, 380]

UPPER_LIP = 13
LOWER_LIP = 14
LEFT_LIP  = 61
RIGHT_LIP = 291

POSE_POINTS = [1, 152, 33, 263, 61, 291]

EAR_THRESHOLD = 0.20
MAR_THRESHOLD = 0.60
YAW_THRESHOLD = 15
PITCH_THRESHOLD = 15


def calculate_ear(landmarks, eye_indices, w, h):
    pts = []
    for i in eye_indices:
        lm = landmarks.landmark[i]
        pts.append((lm.x * w, lm.y * h))

    p0, p1, p2, p3, p4, p5 = pts

    d1 = hypot(p1[0]-p5[0], p1[1]-p5[1])
    d2 = hypot(p2[0]-p4[0], p2[1]-p4[1])
    dH = hypot(p0[0]-p3[0], p0[1]-p3[1])

    if dH == 0:
        return 0

    return (d1 + d2) / (2.0 * dH)


def calculate_mar(landmarks, w, h):
    up = landmarks.landmark[UPPER_LIP]
    lo = landmarks.landmark[LOWER_LIP]
    le = landmarks.landmark[LEFT_LIP]
    ri = landmarks.landmark[RIGHT_LIP]

    v = hypot((up.x-lo.x)*w, (up.y-lo.y)*h)
    h = hypot((le.x-ri.x)*w, (le.y-ri.y)*h)

    if h == 0:
        return 0

    return v / h


def get_head_pose(landmarks, width, height):
    pts_2d = []
    for i in POSE_POINTS:
        lm = landmarks.landmark[i]
        pts_2d.append([lm.x * width, lm.y * height])
    pts_2d = np.array(pts_2d, dtype=np.float64)

    pts_3d = np.array([
        (0.0, 0.0, 0.0),
        (0.0, -120.0, -20.0),
        (-60.0, 40.0, -60.0),
        (60.0, 40.0, -60.0),
        (-40.0, -50.0, -50.0),
        (40.0, -50.0, -50.0)
    ])

    focal_length = width
    cam_matrix = np.array([[focal_length, 0, width/2],
                           [0, focal_length, height/2],
                           [0, 0, 1]])

    dist_coeffs = np.zeros((4, 1))

    success, rvec, tvec = cv2.solvePnP(pts_3d, pts_2d, cam_matrix, dist_coeffs)
    rot_mat, _ = cv2.Rodrigues(rvec)
    sy = np.sqrt(rot_mat[0, 0] ** 2 + rot_mat[1, 0] ** 2)

    pitch = np.degrees(np.arctan2(rot_mat[2, 1], rot_mat[2, 2]))
    yaw = np.degrees(np.arctan2(-rot_mat[2, 0], sy))
    roll = np.degrees(np.arctan2(rot_mat[1, 0], rot_mat[0, 0]))

    return pitch, yaw, roll


class AttentionProcessor:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.attention_history = []
        self.max_history = 30

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        global_score = 0
        status = "Sin Rostro"

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]

            ear_r = calculate_ear(lm, RIGHT_EYE, w, h)
            ear_l = calculate_ear(lm, LEFT_EYE, w, h)
            ear = (ear_r + ear_l) / 2.0

            mar = calculate_mar(lm, w, h)
            pitch, yaw, roll = get_head_pose(lm, w, h)

            score = 1
            status = "Atento"

            if ear < EAR_THRESHOLD:
                score = -10
                status = "Somnolencia (Ojos Cerrados)"
            elif mar > MAR_THRESHOLD:
                score = -10
                status = "Bostezo"
            elif abs(yaw) > YAW_THRESHOLD or abs(pitch) > PITCH_THRESHOLD:
                score = -5
                status = "Distracción"

            self.attention_history.append(score)
            if len(self.attention_history) > self.max_history:
                self.attention_history.pop(0)

            avg = np.mean(self.attention_history)

            if avg > 0:
                global_status = "Nivel Alto"
                color = (0, 255, 0)
            elif avg > -5:
                global_status = "Nivel Medio"
                color = (0, 255, 255)
            else:
                global_status = "Nivel Bajo"
                color = (0, 0, 255)

            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Pose P:{pitch:.1f} Y:{yaw:.1f}",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.putText(frame, f"Estado: {status}", (10, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255) if score < 0 else (0, 255, 0), 2)

            cv2.putText(frame, f"Atención Global: {global_status} ({avg:.1f})",
                        (w - 380, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        color, 2)

        return frame, status, global_score
