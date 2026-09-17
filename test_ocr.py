import cv2
from backend.ocr_engine import OCREngine


ocr = OCREngine()

camera = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)


if not camera.isOpened():

    print("Could not open camera.")
    exit()


print("Camera ready.")
print("Point the camera at text.")
print("Press O to read the text.")
print("Press Q to quit.")


while True:

    success, frame = camera.read()

    if not success:

        print("Could not read frame.")
        break


    cv2.imshow(
        "OCR Test",
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("o"):

        print("\nReading text...")

        text = ocr.read_frame(
            frame
        )

        if text:

            print(
                f"DETECTED TEXT: {text}"
            )

        else:

            print(
                "No readable text detected."
            )


    if key == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()
