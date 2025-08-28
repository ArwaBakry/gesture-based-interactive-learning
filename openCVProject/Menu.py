import cv2
import HandTrackingModule as Htm
import os
import time
import VirtualPainter as Painter
import Slideshow as Slide
import VolumeControl as Volume
import Freeze as freeze
import ManageableAsset as Asset


class MenuNavigator:
    def __init__(self):
        self.folderPath = "Menu"
        self.myList = os.listdir(self.folderPath)
        self.overlayList = [cv2.imread(f'{self.folderPath}/{imPath}') for imPath in self.myList]
        self.header = self.overlayList[5]
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.pTime = 0
        self.detector = Htm.handDetector(detection_con=0.85)

    def navigate_menu(self):
        delay_time = 0.5  # Delay time as needed (in seconds)

        while True:
            success, img = self.cap.read()
            img = cv2.flip(img, 1)
            img[0:107, 0:1280] = self.header
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]
                fingers = self.detector.fingersUp()

                if fingers[1] and fingers[2]:
                    xp, yp = 0, 0
                    print("Selection Mode")
                    if y1 < 107:
                        if 0 < x1 < 100:
                            self.header = self.overlayList[1]
                            self.open_asset()
                        elif 280 < x1 < 380:
                            self.header = self.overlayList[2]
                            self.open_virtual_painter()
                        elif 550 < x1 < 645:
                            self.header = self.overlayList[3]
                            self.open_virtual_presentation()
                        elif 860 < x1 < 955:
                            self.header = self.overlayList[4]
                            self.open_volume_controller()
                        elif 1170 < x1 < 1265:
                            self.header = self.overlayList[5]
                            self.open_pause()

            # Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime

            cv2.putText(img, f'Developer Mode - FPS:{int(fps)}', (440, 710), cv2.FONT_HERSHEY_COMPLEX, 1, (153, 136, 119), 2)
            cv2.imshow("Menu Overlay", img)

            if cv2.waitKey(1) & 0xFF == ord('c'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def open_virtual_painter(self):
        self.cap.release()
        cv2.destroyAllWindows()
        virtual_painter = Painter.VirtualPainter()
        virtual_painter.paint()
        navigator = MenuNavigator()
        navigator.navigate_menu()

    def open_virtual_presentation(self):
        self.cap.release()
        cv2.destroyAllWindows()
        presentation = Slide.VirtualPresentation()
        presentation.virtual_painting()
        navigator = MenuNavigator()
        navigator.navigate_menu()

    def open_volume_controller(self):
        self.cap.release()
        cv2.destroyAllWindows()
        volume_controller = Volume.VolumeController()
        volume_controller.control_volume()
        navigator = MenuNavigator()
        navigator.navigate_menu()

    def open_pause(self):
        self.cap.release()
        cv2.destroyAllWindows()
        pause = freeze.ScreenFreezer()
        pause.main()
        navigator = MenuNavigator()
        navigator.navigate_menu()

    def open_asset(self):
        self.cap.release()
        cv2.destroyAllWindows()
        asset = Asset.DragAndDrop()
        asset.drag_and_drop()
        navigator = MenuNavigator()
        navigator.navigate_menu()


# Usage
if __name__ == "__main__":
    navigator = MenuNavigator()
    navigator.navigate_menu()
