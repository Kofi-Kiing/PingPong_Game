import cv2
import os
import mediapipe as mp
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

class mpHands:
    def __init__(self, maxHands=2, tol1=0.5, tol2=0.5):
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')
        base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=maxHands,
            min_hand_detection_confidence=tol1,
            min_tracking_confidence=tol2)
        self.hands = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.frame_timestamp_ms = 0

    def Marks(self, frame):
        myHands = []
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frameRGB)
        self.frame_timestamp_ms += 33
        results = self.hands.detect_for_video(mp_image, self.frame_timestamp_ms)
        if results.hand_landmarks:
            for handLandmarks in results.hand_landmarks:
                myHand = []
                for landMark in handLandmarks:
                    myHand.append((int(landMark.x * width), int(landMark.y * height)))
                myHands.append(myHand)
        return myHands

width = 1280
height = 720
paddleWidth = 125
paddleHeight = 25
paddleColor = (0, 0, 255)
ballRadius = 15
ballColor = (255, 0, 0)
indexFingPos = 8
font = cv2.FONT_HERSHEY_SIMPLEX

game_state = {
    "xPos": int(width / 2),
    "yPos": int(height / 2),
    "DeltaX": 1,
    "DeltaY": 1,
    "score": 0,
    "lives": 5,
    "running": True
}

def reset_game():
    game_state["xPos"] = int(width / 2)
    game_state["yPos"] = int(height / 2)
    game_state["DeltaX"] = 1
    game_state["DeltaY"] = 1
    game_state["score"] = 0
    game_state["lives"] = 5
    game_state["running"] = True

def generate_frames():
    cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cam.set(cv2.CAP_PROP_FPS, 30)
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    for _ in range(30):
        cam.read()

    findHands = mpHands(2, .5, .5)

    while True:
        ignore, frame = cam.read()
        if not ignore:
            continue
        frame = cv2.resize(frame, (width, height))

        cv2.circle(frame, (game_state["xPos"], game_state["yPos"]), ballRadius, ballColor, -1)
        cv2.putText(frame, str(game_state["score"]), (25, int(6 * paddleHeight)), font, 6, paddleColor, 5)
        cv2.putText(frame, str(game_state["lives"]), (int(width - 125), int(6 * paddleHeight)), font, 6, paddleColor, 5)

        handData = findHands.Marks(frame)
        hand = None
        for h in handData:
            hand = h
            cv2.rectangle(frame,
                          (int(h[8][0] - paddleWidth / 2), 0),
                          (int(h[8][0] + paddleWidth / 2), paddleHeight),
                          paddleColor, -1)

        topEdgeBall = game_state["yPos"] - ballRadius
        bottomEdgeBall = game_state["yPos"] + ballRadius
        leftEdgeBall = game_state["xPos"] - ballRadius
        rightEdgeBall = game_state["xPos"] + ballRadius

        if leftEdgeBall <= 0 or rightEdgeBall >= width:
            game_state["DeltaX"] *= -1
        if bottomEdgeBall >= height:
            game_state["DeltaY"] *= -1

        if topEdgeBall <= paddleHeight and hand:
            if game_state["xPos"] >= int(hand[indexFingPos][0] - paddleWidth / 2) and game_state["xPos"] < (hand[indexFingPos][0] + paddleWidth / 2):
                game_state["DeltaY"] *= -1
                game_state["score"] += 1
                socketio.emit("game_update", {"score": game_state["score"], "lives": game_state["lives"]})
                if game_state["score"] in [1, 10, 15, 20]:
                    game_state["DeltaY"] *= 6
                    game_state["DeltaX"] *= 6
            else:
                game_state["xPos"] = int(width / 2)
                game_state["yPos"] = int(height / 2)
                game_state["lives"] -= 1
                socketio.emit("game_update", {"score": game_state["score"], "lives": game_state["lives"]})

        game_state["xPos"] += game_state["DeltaX"]
        game_state["yPos"] += game_state["DeltaY"]

        if game_state["lives"] == 0:
            cv2.putText(frame, "Game Over!", (200, int(height / 2)), font, 6, (0, 0, 255), 6)
            _, buffer = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            socketio.emit("game_over", {"score": game_state["score"]})
            reset_game()
            continue

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    cam.release()

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/game")
def game():
    return render_template("stream.html")

@app.route("/gameover")
def gameover():
    score = request.args.get("score", 0)
    return render_template("gameover.html", score=score)

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001, use_reloader=False)