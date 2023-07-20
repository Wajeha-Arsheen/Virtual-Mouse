import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import mouse
import threading
######################
wCam, hCam = 640, 480
frameR = 100     #Frame Reduction
smoothening = 7  #random value
######################
l_delay = 0
r_delay = 0
double_delay = 0

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

# print(wScr, hScr)

def l_clk_delay():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay = 0
    l_clk_thread = threading.Thread(target=l_clk_delay)

def r_clk_delay():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target=r_clk_delay)

l_clk_thread = threading.Thread(target=l_clk_delay)
r_clk_thread = threading.Thread(target=r_clk_delay)



while True:
    # Step0.1: Find the landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # Step0.2: Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Step0.3: Check which fingers are up
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        # Step1: Only Index Finger: Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:

            # Step5: Convert the coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            # Step6: Smooth Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Step7: Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

    # Step8: Both Index and middle are up: Clicking Mode
        if fingers[0] == 1 and fingers[1] == 0 and l_delay == 0:

            # Step9: Find distance between fingers
            length, img, lineInfo = detector.findDistance(3, 4, img)

            # Step10: Click mouse if distance short
            cv2.circle(img, (lineInfo[3], lineInfo[4]), 15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()
            l_delay = 1
            l_clk_thread.start()


    #step9: Right Click 
        if fingers[2]==1 and fingers[1]==0 and fingers[0]==0 and fingers[4]==0 and r_delay == 0:
            length, img, lineInfo = detector.findDistance(11, 12, img)
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
            r_delay = 1
            r_clk_thread.start()

            
     # Mouse Scrolling
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:
            if abs(x1 - x2) < 10:
                mouse.wheel(delta=-1)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
            if abs(x1 - x2) < 10:
                mouse.wheel(delta=1)

    # Step11: Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    # Step12: Display
    cv2.imshow("Image", img)
    cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()