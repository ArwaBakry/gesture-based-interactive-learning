import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import os
import time


class DragAndDrop:
    def __init__(self, path="Assets"):
        self.path = path
        self.listImg = self.load_images()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.pTime = 0
        self.detector = HandDetector(detectionCon=0.8)

    def load_images(self):
        myList = os.listdir(self.path)
        listImg = []
        for x, pathImg in enumerate(myList):
            if 'png' in pathImg:
                imgType = 'png'
            else:
                imgType = 'jpg'
            listImg.append(DragImage(f'{self.path}/{pathImg}', [50 + x * 200, 10], imgType))
        listImg.append(DragImage("7.png", [10, 60], "png"))
        return listImg

    def drag_and_drop(self):
        while True:
            success, img = self.cap.read()
            img = cv2.flip(img, 1)
            hands, img = self.detector.findHands(img, flipType=False)

            if hands:
                lmList = hands[0]['lmList']
                myHand = hands[0]  # Get the data for the first detected hand
                fingers = self.detector.fingersUp(myHand)  # Pass the hand data to fingersUp()

                if fingers[1] and fingers[2]:
                    cursor = lmList[8]
                    for imgObject in self.listImg:
                        imgObject.update(cursor)
                else:
                    # Keep the previous positions if fingers are not open
                    for imgObject in self.listImg:
                        cursor = imgObject.posOrigin

            try:
                for imgObject in self.listImg:
                    h, w = imgObject.size
                    ox, oy = imgObject.posOrigin
                    if imgObject.imgType == "png":
                        img = cvzone.overlayPNG(img, imgObject.img, [ox, oy])
                    else:
                        img[oy: oy + h, ox: ox + w] = imgObject.img

            except Exception as e:
                print(f"An error occurred: {e}")

            # Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime

            cv2.putText(img, f'Developer Mode - FPS:{int(fps)}', (440, 710), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (153, 136, 119), 2)
            cv2.imshow("Control Asset", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


class DragImage:
    def __init__(self, path, posOrigin, imgType):
        self.posOrigin = posOrigin
        self.path = path
        self.imgType = imgType

        if self.imgType == 'png':
            self.img = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
        else:
            self.img = cv2.imread(self.path)

        self.size = self.img.shape[:2]

    def update(self, cursor):
        ox, oy = self.posOrigin
        h, w = self.size
        # Check if in region
        if ox < cursor[0] < ox + w and oy < cursor[1] < oy + h:
            self.posOrigin = cursor[0] - w // 2, cursor[1] - h // 2


# Usage
if __name__ == "__main__":
    navigator = DragAndDrop()
    navigator.drag_and_drop()