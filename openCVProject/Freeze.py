import cv2
import time
import HandTrackingModule as Htm


class ScreenFreezer:
    def __init__(self):
        self.detector = Htm.handDetector()
        self.freeze_enabled = True  # Flag
        self.p_time = 0
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

    def toggle_freeze(self):
        if self.freeze_enabled:
            self.freeze_enabled = False
            print("Screen unfrozen")
        else:
            self.freeze_enabled = True
            print("Screen frozen")

        return self.freeze_enabled

    def detect_gesture(self, img):
        if not self.freeze_enabled:
            img = self.detector.findHands(img)
        return img

    def main(self):
        while True:
            success, img = self.cap.read()

            # Flip the image horizontally for mirror effect
            img = cv2.flip(img, 1)

            # Detect hand gestures
            img = self.detect_gesture(img)

            # Calculate FPS
            c_time = time.time()
            fps = 1 / (c_time - self.p_time)
            self.p_time = c_time

            # Display FPS
            cv2.putText(img, f'Developer Mode - FPS:{int(fps)}', (440, 710), cv2.FONT_HERSHEY_COMPLEX, 1, (153, 136, 119), 2)

            # Display hand tracking window
            cv2.imshow("Pause", img)

            # Handle key press events
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('f'):
                self.toggle_freeze()

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
