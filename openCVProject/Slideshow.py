import cv2
import numpy as np
import os
import HandTrackingModule as Htm


class VirtualPresentation:
    def __init__(self):
        # Exact same size is needed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # Get the list of presentation images
        self.folderPath = "Slides"
        self.pathImages = sorted(os.listdir(self.folderPath), key=len)

        self.imgNumber = 0
        self.gestureThreshold = 300
        self.buttonPressed = False
        self.buttonCounter = 0
        self.buttonDelay = 30
        self.annotationNumber = -1
        self.annotationStart = False
        self.annotations = [[]]

        self.detector = Htm.handDetector(detection_con=0.8, max_hands=2)

    def virtual_painting(self):
        while True:
            # Import the image
            success, img = self.cap.read()

            # Flip the image horizontally for mirror effect
            img = cv2.flip(img, 1)

            pathFullImage = os.path.join(self.folderPath, self.pathImages[self.imgNumber])
            imgCurrent = cv2.imread(pathFullImage)

            cv2.line(img, (0, self.gestureThreshold), (1280, self.gestureThreshold), (0, 255, 0), 10)

            # Find hand landmarks
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0 and not self.buttonPressed:
                # tip of index and middle fingers
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # Constrain values for easier drawing
                width, height = 1280, 720
                xVal = int(np.interp(lmList[8][0], [width // 2, 213], [0, width]))
                yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
                x, y = xVal, yVal

                # Check which fingers are up
                fingers = self.detector.fingersUp()

                # Gesture detection
                if y1 <= self.gestureThreshold and y2 <= self.gestureThreshold:
                    # Gesture 1 - Left
                    if fingers == [0, 0, 0, 0, 0]:
                        print("Left")
                        if self.imgNumber > 0:
                            self.buttonPressed = True
                            self.annotations = [[]]
                            self.annotationNumber = -1
                            self.annotationStart = False
                            self.imgNumber -= 1

                    # Gesture 2 - Right
                    elif fingers == [0, 0, 0, 0, 1]:
                        print("Right")
                        if self.imgNumber < len(self.pathImages) - 1:
                            self.buttonPressed = True
                            self.annotations = [[]]
                            self.annotationNumber = -1
                            self.annotationStart = False
                            self.imgNumber += 1

                # Gesture 3 - Show pointer
                if fingers == [0, 1, 1, 0, 0]:
                    x, y = lmList[8][1:]
                    cv2.circle(imgCurrent, (x, y), 12, (0, 0, 255), cv2.FILLED)

                # Gesture 4 - Draw pointer
                if fingers == [0, 1, 0, 0, 0]:
                    if not self.annotationStart:
                        self.annotationStart = True
                        self.annotationNumber += 1
                        self.annotations.append([])
                    x, y = lmList[8][1:]
                    cv2.circle(imgCurrent, (x, y), 12, (0, 0, 255), cv2.FILLED)
                    self.annotations[self.annotationNumber].append((x, y))
                else:
                    self.annotationStart = False

                # Gesture 5 - Erase
                if fingers == [0, 1, 1, 1, 0]:
                    if self.annotations:
                        self.annotations.pop(-1)
                        self.annotationNumber -= 1
                        self.buttonPressed = True

            # Button pressed iterations
            if self.buttonPressed:
                self.buttonCounter += 1
                if self.buttonCounter > self.buttonDelay:
                    self.buttonCounter = 0
                    self.buttonPressed = False

            for i in range(len(self.annotations)):
                for j in range(len(self.annotations[i])):
                    if j != 0:
                        cv2.line(imgCurrent, self.annotations[i][j - 1], self.annotations[i][j], (0, 0, 200), 12)

            # Adding webcam on the slides
            imgSmall = cv2.resize(img, (213, 120))
            h, w, _ = imgCurrent.shape
            imgCurrent[0:120, w - 213:w] = imgSmall

            cv2.imshow("Slides", imgCurrent)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

