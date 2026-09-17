import time


class AlertManager:

    def __init__(self):

        self.alerts = {}

        self.cooldown = 4.0

        self.escalation_cooldown = 1.5

        self.minimum_risk = 60


    def should_alert(
        self,
        track_id,
        risk_level,
        risk_score,
        object_name,
        direction,
        ttc
    ):

        if risk_score < self.minimum_risk:

            return False


        current_time = time.time()

        previous = self.alerts.get(
            track_id
        )


        if previous is None:

            self.alerts[track_id] = {

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "time":
                    current_time
            }

            return True


        previous_level = (
            previous[
                "risk_level"
            ]
        )

        previous_time = (
            previous[
                "time"
            ]
        )

        elapsed = (
            current_time -
            previous_time
        )


        levels = {

            "SAFE": 0,

            "CAUTION": 1,

            "WARNING": 2,

            "CRITICAL": 3
        }


        previous_value = (
            levels.get(
                previous_level,
                0
            )
        )

        current_value = (
            levels.get(
                risk_level,
                0
            )
        )


        if current_value > previous_value:

            self.alerts[track_id] = {

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "time":
                    current_time
            }

            return True


        if (
            risk_level == "CRITICAL"
            and
            elapsed >=
            self.escalation_cooldown
        ):

            self.alerts[track_id] = {

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "time":
                    current_time
            }

            return True


        if elapsed >= self.cooldown:

            self.alerts[track_id] = {

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "time":
                    current_time
            }

            return True


        return False


    def create_message(
        self,
        object_name,
        direction,
        distance,
        risk_level,
        ttc,
        approach,
        path_status
    ):

        object_name = (
            object_name.lower()
        )


        if direction == "CENTER":

            location = (
                "directly ahead"
            )

        else:

            location = (
                f"on your "
                f"{direction.lower()}"
            )


        if risk_level == "CRITICAL":

            prefix = "Danger."

        elif risk_level == "WARNING":

            prefix = "Warning."

        else:

            prefix = "Caution."


        if (
            approach ==
            "APPROACHING"
            and
            path_status ==
            "IN_PATH"
        ):

            message = (

                f"{prefix} "

                f"A {object_name} is "

                f"approaching "

                f"{location}."
            )


        elif (
            ttc is not None
            and
            ttc < 2.0
        ):

            message = (

                f"{prefix} "

                f"A {object_name} is "

                f"very close "

                f"{location}."
            )


        elif path_status == "IN_PATH":

            message = (

                f"{prefix} "

                f"A {object_name} "

                f"is in your path "

                f"{location}."
            )


        elif approach == "APPROACHING":

            message = (

                f"{prefix} "

                f"A {object_name} is "

                f"approaching "

                f"{location}."
            )


        else:

            message = (

                f"{prefix} "

                f"A {object_name} is "

                f"{location}."
            )


        if (
            ttc is not None
            and
            ttc < 3.0
        ):

            message += (

                f" Estimated time to "

                f"interaction is "

                f"{ttc:.1f} seconds."
            )


        return message


    def cleanup(
        self,
        active_ids
    ):

        active_ids = set(
            active_ids
        )


        missing_ids = [

            track_id

            for track_id in self.alerts

            if track_id not in active_ids
        ]


        for track_id in missing_ids:

            del self.alerts[
                track_id
            ]
