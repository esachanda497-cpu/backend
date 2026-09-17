from backend.voice_input import VoiceInput
from backend.intent import detect_intent
from backend.intent import extract_object
import time


class VoiceAssistant:

    def __init__(
        self,
        scene,
        alert_queue
    ):

        self.scene = scene

        self.alert_queue = alert_queue

        self.voice_input = VoiceInput()

        self.running = True

        self.last_object = None

        self.last_direction = None


    def create_response(
        self,
        text
    ):

        intent = detect_intent(
            text
        )


        if intent == "EXIT":

            return None, False


        if intent == "FRONT_QUERY":

            self.last_direction = "CENTER"

            objects = (
                self.scene.get_by_direction(
                    "CENTER"
                )
            )

            self.last_object = (
                objects[0]["object"]
                if objects
                else None
            )

            response = (
                self.scene.describe_direction(
                    "CENTER"
                )
            )

            return response, True


        if intent == "LEFT_QUERY":

            self.last_direction = "LEFT"

            objects = (
                self.scene.get_by_direction(
                    "LEFT"
                )
            )

            self.last_object = (
                objects[0]["object"]
                if objects
                else None
            )

            response = (
                self.scene.describe_direction(
                    "LEFT"
                )
            )

            return response, True


        if intent == "RIGHT_QUERY":

            self.last_direction = "RIGHT"

            objects = (
                self.scene.get_by_direction(
                    "RIGHT"
                )
            )

            self.last_object = (
                objects[0]["object"]
                if objects
                else None
            )

            response = (
                self.scene.describe_direction(
                    "RIGHT"
                )
            )

            return response, True


        if intent == "SCENE_QUERY":

            response = (
                self.scene.describe_scene()
            )

            objects = (
                self.scene.get_all_objects()
            )

            if objects:

                objects.sort(
                    key=lambda data:
                        data.get(
                            "risk_score",
                            0
                        ),
                    reverse=True
                )

                self.last_object = (
                    objects[0]["object"]
                )

                self.last_direction = (
                    objects[0]["direction"]
                )

            return response, True


        if intent == "APPROACHING_QUERY":

            objects = (
                self.scene.get_approaching_objects()
            )

            if not objects:

                return (
                    "Nothing detected is "
                    "currently approaching.",
                    True
                )

            objects.sort(
                key=lambda data:
                    data.get(
                        "risk_score",
                        0
                    ),
                reverse=True
            )

            descriptions = []

            for data in objects:

                descriptions.append(
                    self.scene.create_description(
                        data
                    )
                )

            response = self.format_list(
                "Yes. I detect ",
                descriptions
            )

            self.last_object = (
                objects[0]["object"]
            )

            self.last_direction = (
                objects[0]["direction"]
            )

            return response, True


        if intent == "MOVING_AWAY_QUERY":

            objects = (
                self.scene.get_moving_away_objects()
            )

            if not objects:

                return (
                    "Nothing detected is "
                    "currently moving away.",
                    True
                )

            objects.sort(
                key=lambda data:
                    data.get(
                        "risk_score",
                        0
                    ),
                reverse=True
            )

            descriptions = []

            for data in objects:

                descriptions.append(
                    self.scene.create_description(
                        data
                    )
                )

            response = self.format_list(
                "Yes. I detect ",
                descriptions
            )

            self.last_object = (
                objects[0]["object"]
            )

            self.last_direction = (
                objects[0]["direction"]
            )

            return response, True


        if intent == "LEFT_APPROACHING_QUERY":

            response = (
                self.direction_movement_response(
                    "LEFT",
                    "APPROACHING"
                )
            )

            return response, True


        if intent == "RIGHT_APPROACHING_QUERY":

            response = (
                self.direction_movement_response(
                    "RIGHT",
                    "APPROACHING"
                )
            )

            return response, True


        if intent == "LEFT_MOVING_AWAY_QUERY":

            response = (
                self.direction_movement_response(
                    "LEFT",
                    "MOVING AWAY"
                )
            )

            return response, True


        if intent == "RIGHT_MOVING_AWAY_QUERY":

            response = (
                self.direction_movement_response(
                    "RIGHT",
                    "MOVING AWAY"
                )
            )

            return response, True


        if intent == "OBJECT_QUERY":

            object_name = (
                extract_object(
                    text
                )
            )

            if object_name is None:

                if (
                    "that" in text
                    and
                    self.last_object is not None
                ):

                    object_name = (
                        self.last_object
                    )

                else:

                    return (
                        "I could not identify "
                        "the object you asked about.",
                        True
                    )

            objects = (
                self.scene.get_by_object(
                    object_name
                )
            )

            if objects:

                objects.sort(
                    key=lambda data:
                        data.get(
                            "risk_score",
                            0
                        ),
                    reverse=True
                )

                self.last_object = (
                    object_name
                )

                self.last_direction = (
                    objects[0]["direction"]
                )

            response = (
                self.scene.describe_object(
                    object_name
                )
            )

            return response, True


        if intent == "DISTANCE_QUERY":

            object_name = (
                extract_object(
                    text
                )
            )

            if object_name is None:

                object_name = (
                    self.last_object
                )

            if object_name is None:

                return (
                    "Please tell me which "
                    "object you mean.",
                    True
                )

            objects = (
                self.scene.get_by_object(
                    object_name
                )
            )

            if not objects:

                return (
                    f"I do not currently "
                    f"see a {object_name}.",
                    True
                )

            objects.sort(
                key=lambda data:
                    data.get(
                        "risk_score",
                        0
                    ),
                reverse=True
            )

            data = objects[0]

            distance = (
                data.get(
                    "distance_meters"
                )
            )

            if distance is None:

                return (
                    f"I can see the "
                    f"{object_name}, but I "
                    f"cannot estimate its "
                    f"distance yet.",
                    True
                )

            self.last_object = (
                object_name
            )

            self.last_direction = (
                data["direction"]
            )

            return (
                f"The {object_name} is "
                f"approximately "
                f"{distance:.1f} meters away.",
                True
            )


        if intent == "OCR_QUERY":

            return (
                "Text reading is not "
                "available yet.",
                True
            )


        return (
            "I did not understand "
            "that command.",
            True
        )


    def direction_movement_response(
        self,
        direction,
        movement
    ):

        objects = (
            self.scene.get_by_direction(
                direction
            )
        )

        objects = [
            data
            for data in objects
            if data.get(
                "approach"
            ) == movement
            or data.get(
                "movement"
            ) == movement
        ]

        if not objects:

            if movement == "APPROACHING":

                movement_text = (
                    "approaching"
                )

            else:

                movement_text = (
                    "moving away"
                )

            return (
                f"I do not currently "
                f"detect anything "
                f"{movement_text} on your "
                f"{direction.lower()}."
            )


        objects.sort(
            key=lambda data:
                data.get(
                    "risk_score",
                    0
                ),
            reverse=True
        )


        descriptions = []

        for data in objects:

            descriptions.append(
                self.scene.create_description(
                    data
                )
            )


        self.last_object = (
            objects[0]["object"]
        )

        self.last_direction = (
            direction
        )


        return self.format_list(
            "Yes. ",
            descriptions
        )


    def format_list(
        self,
        prefix,
        descriptions
    ):

        if not descriptions:

            return prefix.strip()


        if len(descriptions) == 1:

            return (
                prefix +
                descriptions[0] +
                "."
            )


        if len(descriptions) == 2:

            return (
                prefix +
                descriptions[0] +
                " and " +
                descriptions[1] +
                "."
            )


        return (
            prefix +
            ", ".join(
                descriptions[:-1]
            ) +
            ", and " +
            descriptions[-1] +
            "."
        )


    def run(self):

        while self.running:

            text = (
                self.voice_input.listen()
            )

            if text is None:

                continue


            response, should_continue = (
                self.create_response(
                    text
                )
            )


            if not should_continue:

                self.running = False

                break


            if response:

                print(
                    f"\nASSISTANT: "
                    f"{response}"
                )

                self.alert_queue.put(
                    (
                        3,
                        response
                    )
                )

                time.sleep(
                    0.8
                )


    def stop(self):

        self.running = False
