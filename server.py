import os
import time
import base64
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from backend.hazard_engine import HazardEngine
from backend.alert_manager import AlertManager

app = FastAPI(title="SafeStep AI")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")

if allowed_origins == "*":
    origins = ["*"]
else:
    origins = [
        origin.strip()
        for origin in allowed_origins.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allowed_origins != "*",
    allow_methods=["*"],
    allow_headers=["*"]
)

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "yolo11n.pt"
)

model = YOLO(MODEL_PATH)

hazard_engine = HazardEngine()

alert_manager = AlertManager()

track_history = {}

reference_heights = {
    "person": 1.70,
    "chair": 0.90,
    "car": 1.50,
    "bus": 3.00,
    "truck": 3.00,
    "bicycle": 1.10,
    "motorcycle": 1.20,
    "dog": 0.60,
    "cat": 0.25,
    "cell phone": 0.15,
    "backpack": 0.50,
    "bottle": 0.25,
    "cup": 0.12
}

focal_length_pixels = 700.0


def decode_frame(data):

    if isinstance(data, bytes):

        encoded = data

    else:

        if "," in data:
            data = data.split(",", 1)[1]

        encoded = base64.b64decode(data)

    array = np.frombuffer(
        encoded,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    return frame


def estimate_distance(
    object_name,
    box_height
):

    if box_height <= 0:
        return None

    reference_height = reference_heights.get(
        object_name.lower()
    )

    if reference_height is None:
        reference_height = 0.50

    distance = (
        reference_height *
        focal_length_pixels
    ) / box_height

    distance = max(
        0.2,
        min(distance, 30.0)
    )

    return round(
        distance,
        2
    )


def get_direction(
    center_x,
    frame_width
):

    normalized_x = (
        center_x /
        frame_width
    )

    if normalized_x < 0.40:
        return "LEFT"

    if normalized_x > 0.60:
        return "RIGHT"

    return "CENTER"


def get_track_state(
    track_id
):

    if track_id not in track_history:

        track_history[track_id] = {
            "distances": [],
            "times": [],
            "positions": [],
            "position_times": []
        }

    return track_history[track_id]


def smooth_distance(
    track_id,
    distance
):

    state = get_track_state(
        track_id
    )

    if distance is None:
        return None

    state["distances"].append(
        distance
    )

    if len(state["distances"]) > 8:

        state["distances"].pop(0)

    return round(
        float(
            np.median(
                state["distances"]
            )
        ),
        2
    )


def calculate_movement(
    track_id,
    distance,
    current_time
):

    state = get_track_state(
        track_id
    )

    if distance is None:
        return 0.0, "STATIONARY"

    if not state["times"]:

        state["times"].append(
            current_time
        )

        state["distances"].append(
            distance
        )

        return 0.0, "STATIONARY"

    previous_time = (
        state["times"][-1]
    )

    previous_distance = (
        state["distances"][-1]
    )

    delta_time = (
        current_time -
        previous_time
    )

    if delta_time <= 0:

        return 0.0, "STATIONARY"

    distance_change = (
        previous_distance -
        distance
    )

    closing_speed = (
        distance_change /
        delta_time
    )

    state["times"].append(
        current_time
    )

    state["distances"].append(
        distance
    )

    if len(state["times"]) > 8:

        state["times"].pop(0)

    if len(state["distances"]) > 8:

        state["distances"].pop(0)

    recent_speeds = []

    if (
        len(state["distances"]) >= 3
        and
        len(state["times"]) >= 3
    ):

        start_index = max(
            1,
            len(state["distances"]) - 4
        )

        for i in range(
            start_index,
            len(state["distances"])
        ):

            dt = (
                state["times"][i] -
                state["times"][i - 1]
            )

            if dt <= 0:
                continue

            speed = (
                state["distances"][i - 1] -
                state["distances"][i]
            ) / dt

            recent_speeds.append(
                speed
            )

    if recent_speeds:

        closing_speed = float(
            np.median(
                recent_speeds
            )
        )

    if closing_speed < 0.20:

        movement = "APPROACHING"

    elif closing_speed > -0.20:

        movement = "MOVING AWAY"

    else:

        movement = "STATIONARY"

    return (
        round(
            closing_speed,
            2
        ),
        movement
    )


def calculate_position_velocity(
    track_id,
    center_x,
    current_time
):

    state = get_track_state(
        track_id
    )

    state["positions"].append(
        center_x
    )

    state["position_times"].append(
        current_time
    )

    if len(state["positions"]) > 8:

        state["positions"].pop(0)

        state["position_times"].pop(0)

    if len(state["positions"]) < 2:

        return 0.0

    previous_x = (
        state["positions"][-2]
    )

    previous_time = (
        state["position_times"][-2]
    )

    delta_time = (
        current_time -
        previous_time
    )

    if delta_time <= 0:

        return 0.0

    velocity_x = (
        center_x -
        previous_x
    ) / delta_time

    return velocity_x


def detect_objects(
    frame
):

    frame_height, frame_width = (
        frame.shape[:2]
    )

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    detections = []

    active_ids = []

    for result in results:

        if result.boxes is None:
            continue

        boxes = result.boxes

        for i in range(
            len(boxes)
        ):

            confidence = float(
                boxes.conf[i]
            )

            if confidence < 0.35:
                continue

            class_id = int(
                boxes.cls[i]
            )

            object_name = model.names[
                class_id
            ]

            coordinates = (
                boxes.xyxy[i]
                .cpu()
                .numpy()
            )

            x1, y1, x2, y2 = (
                coordinates
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            center_x = (
                x1 + x2
            ) / 2

            bottom_y = y2

            box_height = max(
                1,
                y2 - y1
            )

            track_id = None

            if boxes.id is not None:

                track_id = int(
                    boxes.id[i]
                )

            if track_id is None:

                track_id = (
                    f"{object_name}_{i}"
                )

            active_ids.append(
                track_id
            )

            current_time = time.time()

            direction = get_direction(
                center_x,
                frame_width
            )

            raw_distance = (
                estimate_distance(
                    object_name,
                    box_height
                )
            )

            distance = smooth_distance(
                track_id,
                raw_distance
            )

            closing_speed, movement = (
                calculate_movement(
                    track_id,
                    distance,
                    current_time
                )
            )

            velocity_x = (
                calculate_position_velocity(
                    track_id,
                    center_x,
                    current_time
                )
            )

            ttc = (
                hazard_engine.calculate_ttc(
                    distance,
                    closing_speed
                )
            )

            path_status = (
                hazard_engine.walking_path_status(
                    center_x,
                    bottom_y,
                    frame_width,
                    frame_height
                )
            )

            predicted_intersection = (
                hazard_engine.predict_path_intersection(
                    center_x,
                    velocity_x,
                    ttc,
                    frame_width
                )
            )

            hazard = (
                hazard_engine.analyze(
                    object_name,
                    distance,
                    direction,
                    closing_speed,
                    ttc,
                    path_status,
                    predicted_intersection,
                    confidence
                )
            )

            alert = (
                alert_manager.should_alert(
                    track_id,
                    hazard["risk_level"],
                    hazard["risk_score"],
                    object_name,
                    direction,
                    ttc
                )
            )

            detections.append({

                "track_id":
                    track_id,

                "object":
                    object_name,

                "confidence":
                    round(
                        confidence,
                        3
                    ),

                "box":
                    [
                        x1,
                        y1,
                        x2,
                        y2
                    ],

                "center_x":
                    round(
                        center_x,
                        1
                    ),

                "center_y":
                    round(
                        (
                            y1 +
                            y2
                        ) / 2,
                        1
                    ),

                "direction":
                    direction,

                "distance_meters":
                    distance,

                "movement":
                    movement,

                "approach":
                    movement,

                "closing_speed":
                    closing_speed,

                "ttc":
                    hazard["ttc"],

                "ttc_text":
                    hazard["ttc_text"],

                "path_status":
                    path_status,

                "predicted_intersection":
                    predicted_intersection,

                "risk_score":
                    hazard["risk_score"],

                "risk_level":
                    hazard["risk_level"],

                "alert":
                    alert
            })

    alert_manager.cleanup(
        active_ids
    )

    return detections


@app.get("/")
async def root():

    return {

        "status":
            "online",

        "service":
            "SafeStep AI",

        "model":
            MODEL_PATH
    }


@app.head("/")
async def root_head():

    return


@app.get("/health")
async def health():

    return {
        "status":
            "healthy"
    }


@app.websocket("/ws/detect")
async def websocket_detection(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            data = (
                await websocket.receive_text()
            )

            try:

                frame = decode_frame(
                    data
                )

                if frame is None:

                    await websocket.send_json({

                        "error":
                            "Invalid image frame"
                    })

                    continue

                detections = (
                    detect_objects(
                        frame
                    )
                )

                await websocket.send_json({

                    "detections":
                        detections,

                    "timestamp":
                        time.time()
                })

            except Exception as error:

                await websocket.send_json({

                    "error":
                        str(error)
                })

    except WebSocketDisconnect:

        pass

    except Exception:

        pass


@app.websocket("/ws/audio")
async def websocket_audio(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            message = (
                await websocket.receive_json()
            )

            await websocket.send_json({

                "status":
                    "audio_received",

                "message":
                    message
            })

    except WebSocketDisconnect:

        pass

    except Exception:

        pass
