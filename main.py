import math
import random
import cv2
import cvzone
import numpy as np

from cvzone.HandTrackingModule import HandDetector


cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

class GameClass:
    def __init__(self,pathFood):
        self.points = [] #all points of the snake
        self.length = []  #distance between each points
        self.currentLength = 0  #total length of the snake
        self.allowedLength = 150  #total allowed length
        self.previousHead = 0,0  #prev head loc

        self.imgFood = cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood , self.wFood,_ = self.imgFood.shape
        self.foodPoint = 0,0
        self.randFoodLoc()

        self.score =0
        self.finScore=0
        self.gameOver = False

    def randFoodLoc(self):
        self.foodPoint= random.randint(100,1000),random.randint(100,600)


    def update(self,imgMain, curHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain,"Gone ra Botty",[200,300],scale=5,thickness=5,offset=20)
            cvzone.putTextRect(imgMain, f'Nee score ra edi:{self.finScore}',[200,400],scale=5,thickness=5,offset=20)
            cvzone.putTextRect(imgMain, "malli aadalante 'r' nokku bot maxx", [100, 500], scale=3, thickness=3, offset=20)
        else:
            px,py = self.previousHead
            cx,cy = curHead

            self.points.append([cx,cy])
            distance = math.hypot(cx-px,cy-py)
            self.length.append(distance)
            self.currentLength += distance
            self.previousHead = cx,cy

            # length reduction
            if self.currentLength > self.allowedLength:
                for i, len in enumerate(self.length):
                    self.currentLength -= len
                    self.length.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            #check if snake ate the food
            rx, ry = self.foodPoint
            if rx-self.wFood//2<cx<rx+self.wFood//2 and ry-self.hFood//2<cy<ry+self.hFood//2:
                self.randFoodLoc()
                self.allowedLength += 50
                self.score +=1
                print(self.score)



            #Draw snake
            if self.points:
                for i,point in enumerate(self.points):
                    if i!=0:
                        cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,255),20)
                cv2.circle(imgMain,self.points[-1],20,(200,0,200),cv2.FILLED)

            #draw food

            imgMain = cvzone.overlayPNG(imgMain,self.imgFood,(rx-self.wFood//2,ry-self.hFood//2))
            cvzone.putTextRect(imgMain, f'simple score i always beat it:{self.score}', [50, 80], scale=3, thickness=3, offset=10)
            cvzone.putTextRect(imgMain, "High Score : 558", [50, 600], scale=3, thickness=3,
                               offset=10)

            #check for collision

            pts = np.array(self.points[:-2],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(imgMain,[pts],False,(0,200,0),3)
            cv2.pointPolygonTest(pts,(cx,cy),True)
            minDist = cv2.pointPolygonTest(pts,(cx,cy),True)


            if -1<minDist<1:
                self.gameOver = True
                self.points = []  # all points of the snake
                self.length = []  # distance between each points
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed length
                self.previousHead = 0, 0  # prev head loc
                self.randFoodLoc()
                self.finScore = self.score
                self.score = 0

        return imgMain



game = GameClass("img.png")

while True:
    success,img = cap.read()
    img = cv2.flip(img,1)
    hands, img = detector.findHands(img,flipType=False)

    if hands:
        lmList = hands[0]['lmList'] #list of all the points
        pointIndex = lmList[8][0:2]      #gives 3 coordinates xyz
        img = game.update(img,pointIndex)

    cv2.imshow("Image",img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False

