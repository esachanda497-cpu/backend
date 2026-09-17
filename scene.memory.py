import time


class SceneMemory:

    def __init__(self):

        self.objects = {}

        self.memory_timeout = 2.0


    def update(
        self,
        detections
    ):

        current_time = time.time()

        for detection in detections:

            track_id = detection.get(
                "track_id"
            )

            if track_id is None:
                continue

            self.objects[
                track_id
            ] = {
                "track_id":
                    track_id,

                "object":
                    detection.get(
                        "object",
                        "object"
                    ),

                "direction":
                    detection.get(
                        "direction",
                        "CENTER"
                    ),

                "distance_meters":
                    detection.get(
                        "distance_meters"
                    ),

                "movement":
                    detection.get(
                        "movement",
                        "STATIONARY"
                    ),

                "approach":
                    detection.get(
                        "approach",
                        "STATIONARY"
                    ),

                "closing_speed":
                    detection.get(
                        "closing_speed",
                        0.0
                    ),

                "risk_score":
                    detection.get(
                        "risk_score",
                        0.0
                    ),

                "risk_level":
                    detection.get(
                        "risk_level",
                        "SAFE"
                    ),

                "ttc":
                    detection.get(
                        "ttc"
                    ),

                "path_status":
                    detection.get(
                        "path_status",
                        "OUTSIDE_PATH"
                    ),

                "predicted_intersection":
                    detection.get(
                        "predicted_intersection",
                        False
                    ),

                "confidence":
                    detection.get(
                        "confidence",
                        0.0
                    ),

                "time":
                    current_time
            }

        self.cleanup(
            current_time
        )


    def cleanup(
        self,
        current_time=None
    ):

        if current_time is None:
            current_time = time.time()

        expired = []

        for track_id, data in (
            self.objects.items()
        ):

            object_time = data.get(
                "time",
                0
            )

            if (
                current_time -
                object_time
                >
                self.memory_timeout
            ):

                expired.append(
                    track_id
                )

        for track_id in expired:

            del self.objects[
                track_id
            ]


    def get_all_objects(
        self
    ):

        self.cleanup()

        return list(
            self.objects.values()
        )


    def get_by_direction(
        self,
        direction
    ):

        self.cleanup()

        return [
            data
            for data in self.objects.values()
            if data.get(
                "direction"
            ) == direction
        ]


    def get_by_object(
        self,
        object_name
    ):

        self.cleanup()

        object_name = (
            object_name.lower()
        )

        matches = []

        for data in self.objects.values():

            current_object = (
                data.get(
                    "object",
                    ""
                ).lower()
            )

            if (
                current_object ==
                object_name
            ):

                matches.append(
                    data
                )

        return matches


    def get_closest_object(
        self
    ):

        objects = (
            self.get_all_objects()
        )

        objects = [
            data
            for data in objects
            if data.get(
                "distance_meters"
            ) is not None
        ]

        if not objects:
            return None

        objects.sort(
            key=lambda data:
                data[
                    "distance_meters"
                ]
        )

        return objects[0]


    def create_description(
        self,
        data
    ):

        object_name = (
            data.get(
                "object",
                "object"
            )
        )

        direction = (
            data.get(
                "direction",
                "CENTER"
            )
        )

        distance = (
            data.get(
                "distance_meters"
            )
        )

        movement = (
            data.get(
                "movement",
                "STATIONARY"
            )
        )

        if direction == "CENTER":

            direction_text = (
                "directly ahead"
            )

        else:

            direction_text = (
                f"on your "
                f"{direction.lower()}"
            )

        if distance is None:

            distance_text = (
                "an unknown distance away"
            )

        else:

            distance_text = (
                f"approximately "
                f"{distance:.1f} "
                f"meters away"
            )

        if movement == "APPROACHING":

            movement_text = (
                "approaching"
            )

        elif movement == "MOVING AWAY":

            movement_text = (
                "moving away"
            )

        else:

            movement_text = (
                "stationary"
            )

        return (
            f"{object_name} "
            f"{direction_text}, "
            f"{distance_text}, "
            f"{movement_text}"
        )


    def describe_object(
        self,
        object_name
    ):

        objects = (
            self.get_by_object(
                object_name
            )
        )

        if not objects:

            return (
                f"I do not currently "
                f"see a {object_name}."
            )

        objects.sort(
            key=lambda data:
                data.get(
                    "risk_score",
                    0
                ),
            reverse=True
        )

        descriptions = [
            self.create_description(
                data
            )
            for data in objects
        ]

        return self.format_list(
            descriptions
        )


    def describe_direction(
        self,
        direction
    ):

        objects = (
            self.get_by_direction(
                direction
            )
        )

        if not objects:

            if direction == "CENTER":

                return (
                    "I do not currently "
                    "detect anything "
                    "directly ahead."
                )

            return (
                f"I do not currently "
                f"detect anything on "
                f"your {direction.lower()}."
            )

        objects.sort(
            key=lambda data:
                data.get(
                    "risk_score",
                    0
                ),
            reverse=True
        )

        descriptions = [
            self.create_description(
                data
            )
            for data in objects
        ]

        return self.format_list(
            descriptions
        )


    def describe_scene(
        self
    ):

        objects = (
            self.get_all_objects()
        )

        if not objects:

            return (
                "I do not currently "
                "detect any objects."
            )

        objects.sort(
            key=lambda data:
                data.get(
                    "risk_score",
                    0
                ),
            reverse=True
        )

        descriptions = [
            self.create_description(
                data
            )
            for data in objects
        ]

        return self.format_list(
            descriptions
        )


    def format_list(
        self,
        descriptions
    ):

        if not descriptions:
            return ""

        if len(descriptions) == 1:

            return (
                descriptions[0] +
                "."
            )

        if len(descriptions) == 2:

            return (
                descriptions[0] +
                " and " +
                descriptions[1] +
                "."
            )

        return (
            ", ".join(
                descriptions[:-1]
            ) +
            ", and " +
            descriptions[-1] +
            "."
        )


    def get_approaching_objects(
        self
    ):

        objects = (
            self.get_all_objects()
        )

        return [
            data
            for data in objects
            if data.get(
                "movement"
            ) == "APPROACHING"
        ]


    def get_moving_away_objects(
        self
    ):

        objects = (
            self.get_all_objects()
        )

        return [
            data
            for data in objects
            if data.get(
                "movement"
            ) == "MOVING AWAY"
        ]


    def get_highest_risk_object(
        self
    ):

        objects = (
            self.get_all_objects()
        )

        if not objects:
            return None

        objects.sort(
            key=lambda data:
                data.get(
                    "risk_score",
                    0
                ),
            reverse=True
        )

        return objects[0]
