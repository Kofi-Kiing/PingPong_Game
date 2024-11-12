import cv2
print(cv2.__version__)
import time 

class mpHands:
        import mediapipe as mp
        def __init__(self,maxHands=2,tol1=1,tol2=1):
                self.hands=self.mp.solutions.hands.Hands(False,maxHands,)
        def Marks(self,frame):
                myHands=[]
                frameRGB=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                results=self.hands.process(frameRGB)
                if results.multi_hand_landmarks != None:
                    for handLandmarks in results.multi_hand_landmarks:
                        myHand=[]
                        for landMark in handLandmarks.landmark:
                                myHand.append((int(landMark.x*width),int(landMark.y*height)))
                        myHands.append(myHand)
                return myHands                
                                
                                              

width=1280
height=720
cam=cv2.VideoCapture(0,cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cam.set(cv2.CAP_PROP_FPS,30)
cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))

findHands=mpHands(2,.5,.5)
paddleWidth=125
paddleHeight=25
paddleColor=(0,0,255)

ballRadius=15
ballColor=(255,0,0)
xPos=int(width/2)
yPos=int(height/2)
DeltaX=1
DeltaY=1
score=0
lives=5
font=cv2.FONT_HERSHEY_SIMPLEX
indexFingPos=8


while True:
        ignore, frame = cam.read() 
        frame=cv2.resize(frame,(width,height)) 
        cv2.circle(frame, (xPos,yPos), ballRadius,ballColor,-1)
        cv2.putText(frame,str(score),(25,int(6*paddleHeight)),font,6,paddleColor,5)
        cv2.putText(frame,str(lives),(int(width-125),int(6*paddleHeight)),font,6,paddleColor,5)
        

        handData=findHands.Marks(frame) 
        for hand in handData:
            cv2.rectangle(frame,(int(hand[8][0]-paddleWidth/2),0),(int(hand[8][0]+paddleWidth/2),paddleHeight),paddleColor,-1)
        topEdgeBall=yPos-ballRadius  
        bottomEdgeBall=yPos+ballRadius   
        leftEdgeBall=xPos-ballRadius
        rightEdgeBall=xPos+ballRadius
        if leftEdgeBall<=0 or rightEdgeBall>=width:
            DeltaX=DeltaX*(-1)
        if bottomEdgeBall >=height :
            DeltaY=DeltaY*(-1) 

        if topEdgeBall<=paddleHeight:     

            if xPos>=int(hand[indexFingPos][0]-paddleWidth/2) and xPos<(hand[indexFingPos][0]+paddleWidth/2) : #if x position of the ball is greater than the left egde of the paddle and also less than the right edge of the paddle         
                DeltaY=DeltaY*(-1) 
                score=score + 1 
                if score==1 or score==10 or score==15 or score==20:
                    DeltaY=DeltaY*6
                    DeltaX=DeltaX*6
            else:
                xPos=int(width/2)
                yPos=int(height/2)
                lives=lives-1  
        xPos=xPos+DeltaX  
        yPos=yPos+DeltaY         
        cv2.imshow('my Webcam',frame)
        cv2.moveWindow('my Webcam',0,0)
        if lives==0:
            
            #cv2.putText(frame,str("Game Over Loser!!!"),(200,int(height/2)),font,3,(0,0,255),6)  
            
            break
        if cv2.waitKey(1) & 0xff ==ord('q'):
                break
cam.release()        