import easyocr
import cv2
import time


class OCREngine:

    def __init__(self):

        print("Loading OCR engine...")

        self.reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

        self.last_text = ""

        self.last_time = 0

        self.cooldown = 5.0

        print("OCR engine ready.")


    def clean_text(
        self,
        text
    ):

        text = text.strip()

        text = " ".join(
            text.split()
        )

        return text


    def read_frame(
        self,
        frame
    ):

        if frame is None:

            return []


        try:

            results = self.reader.readtext(
                frame,
                detail=1,
                paragraph=False
            )

        except Exception as error:

            print(
                f"OCR error: {error}"
            )

            return []


        detections = []


        for result in results:

            if len(result) < 3:

                continue


            box = result[0]

            text = result[1]

            confidence = float(
                result[2]
            )


            text = self.clean_text(
                text
            )


            if not text:

                continue


            if confidence < 0.40:

                continue


            detections.append(
                {
                    "text": text,

                    "confidence":
                        round(
                            confidence,
                            2
                        ),

                    "box":
                        box
                }
            )


        return detections


    def create_message(
        self,
        detections
    ):

        if not detections:

            return None


        detections = sorted(
            detections,
            key=lambda item:
                item["confidence"],
            reverse=True
        )


        texts = []


        for detection in detections:

            text = detection[
                "text"
            ]

            if text not in texts:

                texts.append(
                    text
                )


        if not texts:

            return None


        message = (
            "I can read: "
            +
            ", ".join(
                texts
            )
        )


        current_time = time.time()


        if (
            message ==
            self.last_text
            and
            current_time -
            self.last_time
            <
            self.cooldown
        ):

            return None


        self.last_text = message
        self.last_time = current_time


        return message
