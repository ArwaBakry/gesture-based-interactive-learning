import cv2
import numpy as np
import time
import os
import HandTrackingModule as Htm


class VirtualPainter:
    def __init__(self):
        self.brushSize = 5  # Default brush size
        self.brushThickness = [10, 5]
        self.eraserThickness = 75
        self.drawColor = (0, 0, 0)
        self.paintColor = [
            (0, 0, 255),
            (215, 115, 0),
            (0, 255, 0),
            (0, 255, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 0, 0)
        ]
        self.pTime = 0

        self.folderPath = "Header"
        self.myList = os.listdir(self.folderPath)
        self.overlayList = []
        for imPath in self.myList:
            image = cv2.imread(f'{self.folderPath}/{imPath}')
            self.overlayList.append(image)
        self.header = self.overlayList[7]

        # Exact same size is needed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        self.detector = Htm.handDetector(detection_con=0.85)
        self.xp, self.yp = 0, 0
        self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    # Function to save canvas as an image
    @staticmethod
    def save_canvas(canvas, filename):
        cv2.imwrite(filename, canvas)
        print("Canvas saved as:", filename)

    def paint(self):
        while True:
            # Import the image
            success, img = self.cap.read()

            # Flip the image horizontally for mirror effect
            img = cv2.flip(img, 1)

            # Find hand landmarks
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                # tip of index and middle fingers
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # Check which fingers are up
                fingers = self.detector.fingersUp()

                # If selection mode - two fingers are up
                if fingers[1] and fingers[2]:
                    self.xp, self.yp = 0, 0
                    print("Selection Mode")
                    # Checking for the click
                    if y1 < 107:
                        if 0 < x1 < 119:
                            self.header = self.overlayList[9]
                            self.brushSize = self.brushThickness[0]
                        elif 120 < x1 < 239:
                            self.header = self.overlayList[10]
                            self.brushSize = self.brushThickness[1]
                        elif 240 < x1 < 315:
                            self.header = self.overlayList[8]
                            self.drawColor = self.paintColor[0]
                        elif 329 < x1 < 404:
                            self.header = self.overlayList[2]
                            self.drawColor = self.paintColor[1]
                        elif 418 < x1 < 493:
                            self.header = self.overlayList[6]
                            self.drawColor = self.paintColor[2]
                        elif 507 < x1 < 582:
                            self.header = self.overlayList[11]
                            self.drawColor = self.paintColor[3]
                        elif 596 < x1 < 671:
                            self.header = self.overlayList[1]
                            self.drawColor = self.paintColor[4]
                        elif 685 < x1 < 760:
                            self.header = self.overlayList[5]
                            self.drawColor = self.paintColor[5]
                        elif 806 < x1 < 897:
                            self.header = self.overlayList[4]
                            self.drawColor = self.paintColor[6]
                        elif 943 < x1 < 1034:
                            self.header = self.overlayList[3]
                            # Reset canvas
                            self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)  # Clear canvas

                cv2.rectangle(img, (x1, y1 - 20), (x2, y2 + 20), self.drawColor, cv2.FILLED)

                # If drawing mode - index finger is up
                if fingers[1] and not fingers[2]:
                    cv2.circle(img, (x1, y1), 15, self.drawColor, cv2.FILLED)
                    print("Drawing Mode")
                    if self.xp == 0 and self.yp == 0:
                        self.xp, self.yp = x1, y1

                    if self.drawColor == (0, 0, 0):
                        cv2.line(img, (self.xp, self.yp), (x1, y1), self.drawColor, self.eraserThickness)
                        cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.drawColor, self.eraserThickness)
                    else:
                        cv2.line(img, (self.xp, self.yp), (x1, y1), self.drawColor, self.brushSize)
                        cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.drawColor, self.brushSize)

                    self.xp, self.yp = x1, y1
                else:
                    # Reset drawing position when not in drawing mode
                    self.xp, self.yp = 0, 0

            imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
            img = cv2.bitwise_and(img, imgInv)
            img = cv2.bitwise_or(img, self.imgCanvas)

            # Setting frame/second
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime

            img[0:107, 0:1280] = self.header
            cv2.putText(img, f'Developer Mode - FPS:{int(fps)}', (440, 710), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (153, 136, 119), 2)
            cv2.imshow("Virtual Painter", img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                timestamp = int(time.time())
                filename = f"canvas_{timestamp}.png"
                self.save_canvas(self.imgCanvas, filename)
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

