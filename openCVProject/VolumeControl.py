import cv2
import time
import numpy as np
import HandTrackingModule as Htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeController:
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        self.volRange = self.volume.GetVolumeRange()
        self.volBar = 470
        self.volPercentage = 0

        self.pTime = 0
        self.detector = Htm.handDetector(detection_con=0.8, max_hands=1)

        self.wCam, self.hCam = 1280, 720
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.wCam)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.hCam)

    def control_volume(self):
        while True:
            success, img = self.cap.read()

            # Flip the image horizontally for mirror effect
            img = cv2.flip(img, 1)

            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                # Find distance between index and thumb
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.line(img, (x1, y1), (x2, y2), (190, 135, 0), 3)
                cv2.circle(img, (cx, cy), 15, (190, 135, 0), cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)

                # Convert Volume
                self.volBar = np.interp(length, [50, 250], [470, 220])
                self.volPercentage = np.interp(length, [50, 250], [0, 100])

                # Reduce resolution to make it smoother
                smoothness = 2
                self.volPercentage = smoothness * round(self.volPercentage / smoothness)

                # Check fingers up
                fingers = self.detector.fingersUp()

                # If pinkie is up determine volume
                if not fingers[4]:
                    self.volume.SetMasterVolumeLevelScalar(self.volPercentage / 100, None)
                    cv2.circle(img, (cx, cy), 15, (0, 190, 190), cv2.FILLED)

            # Drawings
            cv2.rectangle(img, (50, 220), (85, 470), (190, 135, 0), 3)
            cv2.rectangle(img, (50, int(self.volBar)), (85, 470), (190, 135, 0), cv2.FILLED)
            cv2.putText(img, f'Volume {int(self.volPercentage)}%', (10, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (190, 135, 0), 2)
            cVol = int(self.volume.GetMasterVolumeLevelScalar() * 100)
            cv2.putText(img, f'Volume Set {int(cVol)}%', (10, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (190, 135, 0), 2)

            # Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime

            cv2.putText(img, f'Developer Mode - FPS:{int(fps)}', (440, 710), cv2.FONT_HERSHEY_COMPLEX, 1, (153, 136, 119), 2)
            cv2.imshow("Img", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

