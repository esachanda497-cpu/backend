import time
from collections import deque


class AudioEngine:

    def __init__(self):

        self.history = deque(
            maxlen=20
        )

        self.minimum_db = -55.0

        self.minimum_vehicle_score = 0.42

        self.approaching_slope = 1.5

        self.away_slope = -1.5

        self.speech_hold_time = 1.5

        self.speech_active_until = 0

        self.last_result = {
            "sound_detected": False,
            "vehicle_like": False,
            "movement": "STABLE",
            "confidence": 0.0,
            "sound_level": -60.0,
            "low_frequency_ratio": 0.0,
            "speech_detected": False
        }


    def clamp(
        self,
        value,
        minimum,
        maximum
    ):

        return max(
            minimum,
            min(
                value,
                maximum
            )
        )


    def set_speech_detected(
        self,
        detected
    ):

        if detected:

            self.speech_active_until = (
                time.time()
                +
                self.speech_hold_time
            )


    def speech_is_active(self):

        return (
            time.time()
            <
            self.speech_active_until
        )


    def calculate_vehicle_score(
        self,
        sound_level,
        low_frequency_ratio
    ):

        energy_score = self.clamp(
            (
                sound_level -
                self.minimum_db
            ) / 30.0,
            0.0,
            1.0
        )


        low_score = self.clamp(
            (
                low_frequency_ratio -
                0.15
            ) / 0.50,
            0.0,
            1.0
        )


        score = (
            energy_score * 0.45
            +
            low_score * 0.55
        )


        return round(
            score,
            3
        )


    def update(
        self,
        sound_level,
        low_frequency_ratio,
        speech_detected=False
    ):

        current_time = time.time()


        if speech_detected:

            self.set_speech_detected(
                True
            )


        speech_active = (
            self.speech_is_active()
        )


        vehicle_score = (
            self.calculate_vehicle_score(
                sound_level,
                low_frequency_ratio
            )
        )


        sound_detected = (
            sound_level >
            self.minimum_db
        )


        self.history.append(
            {
                "time":
                    current_time,

                "sound_level":
                    sound_level,

                "vehicle_score":
                    vehicle_score
            }
        )


        if speech_active:

            result = {
                "sound_detected":
                    sound_detected,

                "vehicle_like":
                    False,

                "movement":
                    "STABLE",

                "confidence":
                    0.0,

                "sound_level":
                    round(
                        sound_level,
                        2
                    ),

                "low_frequency_ratio":
                    round(
                        low_frequency_ratio,
                        3
                    ),

                "sound_slope":
                    0.0,

                "speech_detected":
                    True
            }


            self.last_result = result

            return result


        if len(
            self.history
        ) < 5:

            result = {
                "sound_detected":
                    sound_detected,

                "vehicle_like":
                    vehicle_score
                    >=
                    self.minimum_vehicle_score,

                "movement":
                    "STABLE",

                "confidence":
                    vehicle_score,

                "sound_level":
                    round(
                        sound_level,
                        2
                    ),

                "low_frequency_ratio":
                    round(
                        low_frequency_ratio,
                        3
                    ),

                "sound_slope":
                    0.0,

                "speech_detected":
                    False
            }


            self.last_result = result

            return result


        recent = list(
            self.history
        )[-10:]


        start_time = (
            recent[0]["time"]
        )


        x_values = [
            item["time"] -
            start_time
            for item in recent
        ]


        y_values = [
            item["sound_level"]
            for item in recent
        ]


        x_mean = (
            sum(x_values)
            /
            len(x_values)
        )


        y_mean = (
            sum(y_values)
            /
            len(y_values)
        )


        numerator = sum(
            (
                x - x_mean
            )
            *
            (
                y - y_mean
            )
            for x, y in zip(
                x_values,
                y_values
            )
        )


        denominator = sum(
            (
                x - x_mean
            ) ** 2
            for x in x_values
        )


        if denominator <= 0:

            slope = 0.0

        else:

            slope = (
                numerator
                /
                denominator
            )


        average_vehicle_score = (
            sum(
                item[
                    "vehicle_score"
                ]
                for item in recent
            )
            /
            len(recent)
        )


        movement = "STABLE"


        if (
            average_vehicle_score
            >=
            self.minimum_vehicle_score
        ):

            if (
                slope
                >=
                self.approaching_slope
            ):

                movement = (
                    "APPROACHING"
                )

            elif (
                slope
                <=
                self.away_slope
            ):

                movement = (
                    "MOVING AWAY"
                )


        confidence = (
            average_vehicle_score
        )


        if movement != "STABLE":

            slope_confidence = self.clamp(
                abs(slope) / 5.0,
                0.0,
                1.0
            )


            confidence = (
                average_vehicle_score
                *
                0.7
                +
                slope_confidence
                *
                0.3
            )


        result = {
            "sound_detected":
                sound_detected,

            "vehicle_like":
                average_vehicle_score
                >=
                self.minimum_vehicle_score,

            "movement":
                movement,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "sound_level":
                round(
                    sound_level,
                    2
                ),

            "low_frequency_ratio":
                round(
                    low_frequency_ratio,
                    3
                ),

            "sound_slope":
                round(
                    slope,
                    2
                ),

            "speech_detected":
                False
        }


        self.last_result = result

        return result
