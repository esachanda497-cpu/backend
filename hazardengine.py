import math


class HazardEngine:

    def __init__(self):

        self.max_prediction_time = 5.0

        self.min_closing_speed = 0.10

        self.critical_ttc = 1.5

        self.warning_ttc = 3.0

        self.caution_ttc = 5.0


    def calculate_distance_speed(
        self,
        previous_distance,
        current_distance,
        delta_time
    ):

        if previous_distance is None:
            return 0.0

        if current_distance is None:
            return 0.0

        if delta_time <= 0:
            return 0.0

        speed = (
            previous_distance -
            current_distance
        ) / delta_time

        return speed


    def calculate_ttc(
        self,
        distance,
        closing_speed
    ):

        if distance is None:
            return None

        if closing_speed <= self.min_closing_speed:
            return None

        ttc = distance / closing_speed

        if ttc < 0:
            return None

        if ttc > self.max_prediction_time:
            return None

        return ttc


    def walking_path_status(
        self,
        center_x,
        bottom_y,
        frame_width,
        frame_height
    ):

        normalized_y = (
            bottom_y /
            frame_height
        )

        normalized_x = (
            center_x /
            frame_width
        )

        path_width = (
            0.18 +
            0.32 * normalized_y
        )

        distance_from_center = abs(
            normalized_x - 0.5
        )

        if distance_from_center < (
            path_width * 0.65
        ):

            return "IN_PATH"

        if distance_from_center < path_width:

            return "NEAR_PATH"

        return "OUTSIDE_PATH"


    def predict_path_intersection(
        self,
        center_x,
        velocity_x,
        ttc,
        frame_width
    ):

        if ttc is None:

            prediction_time = 2.0

        else:

            prediction_time = min(
                ttc,
                self.max_prediction_time
            )

        predicted_x = (
            center_x +
            velocity_x *
            prediction_time
        )

        normalized_x = (
            predicted_x /
            frame_width
        )

        distance_from_center = abs(
            normalized_x - 0.5
        )

        if distance_from_center < 0.28:

            return True

        return False


    def calculate_risk(
        self,
        object_name,
        distance,
        direction,
        closing_speed,
        ttc,
        path_status,
        predicted_intersection,
        confidence
    ):

        score = 0.0

        if distance is not None:

            if distance < 1.0:

                score += 40

            elif distance < 2.0:

                score += 32

            elif distance < 3.0:

                score += 24

            elif distance < 5.0:

                score += 14

            elif distance < 8.0:

                score += 7


        if closing_speed > 0:

            if closing_speed > 2.0:

                score += 25

            elif closing_speed > 1.0:

                score += 20

            elif closing_speed > 0.5:

                score += 14

            elif closing_speed > 0.2:

                score += 7


        if ttc is not None:

            if ttc < 1.0:

                score += 30

            elif ttc < 1.5:

                score += 27

            elif ttc < 2.0:

                score += 23

            elif ttc < 3.0:

                score += 17

            elif ttc < 5.0:

                score += 8


        if path_status == "IN_PATH":

            score += 25

        elif path_status == "NEAR_PATH":

            score += 12


        if predicted_intersection:

            score += 20


        if direction == "CENTER":

            score += 10

        elif direction in [
            "LEFT",
            "RIGHT"
        ]:

            score += 3


        score *= min(
            max(
                confidence,
                0.5
            ),
            1.0
        )

        score = min(
            score,
            100
        )


        if score >= 80:

            level = "CRITICAL"

        elif score >= 60:

            level = "WARNING"

        elif score >= 35:

            level = "CAUTION"

        else:

            level = "SAFE"


        return (
            round(score, 1),
            level
        )


    def analyze(
        self,
        object_name,
        distance,
        direction,
        closing_speed,
        ttc,
        path_status,
        predicted_intersection,
        confidence
    ):

        risk_score, risk_level = (
            self.calculate_risk(
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


        if ttc is None:

            ttc_text = "N/A"

        else:

            ttc_text = (
                f"{ttc:.1f}s"
            )


        return {

            "risk_score":
                risk_score,

            "risk_level":
                risk_level,

            "ttc":
                ttc,

            "ttc_text":
                ttc_text,

            "path_status":
                path_status,

            "predicted_intersection":
                predicted_intersection,

            "closing_speed":
                closing_speed
        }
