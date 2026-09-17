def detect_intent(text):

    if not text:
        return "UNKNOWN"

    text = text.lower().strip()


    exit_phrases = [
        "exit",
        "quit",
        "stop assistant",
        "close assistant",
        "shut down"
    ]

    for phrase in exit_phrases:

        if phrase in text:
            return "EXIT"


    ocr_phrases = [
        "read this",
        "read that",
        "read the text",
        "what does this say",
        "what is written",
        "read the sign",
        "read the label"
    ]

    for phrase in ocr_phrases:

        if phrase in text:
            return "OCR_QUERY"


    left_approaching_phrases = [
        "what is approaching on my left",
        "what's approaching on my left",
        "what is coming from my left",
        "what's coming from my left",
        "is anything approaching on my left",
        "is something approaching on my left",
        "anything approaching on my left"
    ]

    for phrase in left_approaching_phrases:

        if phrase in text:
            return "LEFT_APPROACHING_QUERY"


    right_approaching_phrases = [
        "what is approaching on my right",
        "what's approaching on my right",
        "what is coming from my right",
        "what's coming from my right",
        "is anything approaching on my right",
        "is something approaching on my right",
        "anything approaching on my right"
    ]

    for phrase in right_approaching_phrases:

        if phrase in text:
            return "RIGHT_APPROACHING_QUERY"


    left_away_phrases = [
        "what is moving away on my left",
        "what's moving away on my left",
        "is anything moving away on my left",
        "is something moving away on my left",
        "anything moving away on my left"
    ]

    for phrase in left_away_phrases:

        if phrase in text:
            return "LEFT_MOVING_AWAY_QUERY"


    right_away_phrases = [
        "what is moving away on my right",
        "what's moving away on my right",
        "is anything moving away on my right",
        "is something moving away on my right",
        "anything moving away on my right"
    ]

    for phrase in right_away_phrases:

        if phrase in text:
            return "RIGHT_MOVING_AWAY_QUERY"


    approaching_phrases = [
        "what is approaching",
        "what's approaching",
        "what is coming towards me",
        "what's coming towards me",
        "what is coming toward me",
        "what's coming toward me",
        "is anything approaching",
        "is something approaching",
        "what is getting closer",
        "what's getting closer",
        "is anything getting closer",
        "is something getting closer"
    ]

    for phrase in approaching_phrases:

        if phrase in text:
            return "APPROACHING_QUERY"


    away_phrases = [
        "what is moving away",
        "what's moving away",
        "is anything moving away",
        "is something moving away",
        "what is going away",
        "what's going away",
        "what is getting farther",
        "what's getting farther",
        "is anything getting farther"
    ]

    for phrase in away_phrases:

        if phrase in text:
            return "MOVING_AWAY_QUERY"


    front_phrases = [
        "what is in front of me",
        "what's in front of me",
        "what is ahead of me",
        "what's ahead of me",
        "what is directly ahead",
        "what's directly ahead",
        "what is in front",
        "what's in front",
        "what do i have in front of me"
    ]

    for phrase in front_phrases:

        if phrase in text:
            return "FRONT_QUERY"


    left_phrases = [
        "what is on my left",
        "what's on my left",
        "what is to my left",
        "what's to my left",
        "what do i have on my left",
        "what do i have to my left",
        "anything on my left",
        "anything to my left"
    ]

    for phrase in left_phrases:

        if phrase in text:
            return "LEFT_QUERY"


    right_phrases = [
        "what is on my right",
        "what's on my right",
        "what is to my right",
        "what's to my right",
        "what do i have on my right",
        "what do i have to my right",
        "anything on my right",
        "anything to my right"
    ]

    for phrase in right_phrases:

        if phrase in text:
            return "RIGHT_QUERY"


    scene_phrases = [
        "what do you see",
        "what can you see",
        "describe my surroundings",
        "describe the scene",
        "what is around me",
        "what's around me",
        "what is around",
        "tell me what you see",
        "tell me what is around me",
        "tell me what's around me",
        "give me a description"
    ]

    for phrase in scene_phrases:

        if phrase in text:
            return "SCENE_QUERY"


    distance_phrases = [
        "how far is it",
        "how far away is it",
        "how far is that",
        "how far away is that",
        "what is the distance",
        "what's the distance",
        "how far",
        "distance to"
    ]

    for phrase in distance_phrases:

        if phrase in text:
            return "DISTANCE_QUERY"


    object_phrases = [
        "where is the",
        "where's the",
        "do you see the",
        "can you see the",
        "is there a",
        "is there an",
        "tell me about the",
        "what about the",
        "what about that",
        "where is that",
        "where's that"
    ]

    for phrase in object_phrases:

        if phrase in text:
            return "OBJECT_QUERY"


    return "UNKNOWN"


def extract_object(text):

    if not text:
        return None

    text = text.lower().strip()


    object_names = [

        "person",
        "people",

        "car",
        "truck",
        "bus",
        "motorcycle",
        "bicycle",
        "train",

        "cell phone",
        "phone",

        "laptop",
        "computer",
        "keyboard",
        "mouse",

        "chair",
        "couch",
        "bed",
        "table",

        "bottle",
        "cup",
        "backpack",
        "handbag",
        "suitcase",

        "dog",
        "cat",
        "bird",

        "traffic light",
        "stop sign",
        "bench",
        "parking meter"
    ]


    for object_name in object_names:

        if object_name in text:

            if object_name == "people":
                return "person"

            if object_name == "phone":
                return "cell phone"

            return object_name


    return None
