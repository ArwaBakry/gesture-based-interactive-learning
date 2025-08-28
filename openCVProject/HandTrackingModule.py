import cv2
import mediapipe as mp
import time


class handDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_threshold=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_threshold = track_threshold

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_threshold)
        self.mpDraw = mp.solutions.drawing_utils
        self.finger_tips = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms, hand_type in zip(self.results.multi_hand_landmarks, self.results.multi_handedness):
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

                    # Get bounding box
                    bbox = self.calculate_bounding_box(img, handLms)

                    # Display hand type (Left/Right) in bounding box
                    cv2.putText(img, hand_type.classification[0].label, (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Draw bounding box
                    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 255, 255), 2)

                    # Get hand landmarks positions
                    self.findPosition(img, draw)

        return img

    def calculate_bounding_box(self, img, hand_landmarks):
        # Get bounding box dimensions
        x_min, x_max, y_min, y_max = img.shape[1], 0, img.shape[0], 0

        for lm in hand_landmarks.landmark:
            x, y = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y

        # Expand bounding box
        bbox_width = x_max - x_min
        bbox_height = y_max - y_min
        x_min = max(0, x_min - int(bbox_width * 0.15))
        x_max = min(img.shape[1], x_max + int(bbox_width * 0.15))
        y_min = max(0, y_min - int(bbox_height * 0.15))
        y_max = min(img.shape[0], y_max + int(bbox_height * 0.15))

        return x_min, y_min, x_max - x_min, y_max - y_min

    def findPosition(self, img, draw=True):
        self.lmlist = []
        if hasattr(self, 'results') and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    height, width, channel = img.shape
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    self.lmlist.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 3, (255, 0, 0), cv2.FILLED)

        return self.lmlist

    def fingersUp(self):
        fingers_list = []

        # Thumb
        if self.lmlist[self.finger_tips[0]][1] > self.lmlist[self.finger_tips[0] - 1][1]:
            fingers_list.append(1)
        else:
             fingers_list.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if self.lmlist[self.finger_tips[id]][2] < self.lmlist[self.finger_tips[id] - 2][2]:
                fingers_list.append(1)
            else:
                fingers_list.append(0)

        return fingers_list

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()

        # Flip the image horizontally for mirror effect
        img = cv2.flip(img, 1)

        img = detector.findHands(img)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

        cv2.imshow("Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()