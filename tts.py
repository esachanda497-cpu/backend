import win32com.client
import pythoncom


class Speaker:

    def __init__(self):

        pythoncom.CoInitialize()

        self.voice = (
            win32com.client.Dispatch(
                "SAPI.SpVoice"
            )
        )

        self.voice.Rate = 1

        self.voice.Volume = 100


    def speak(
        self,
        text
    ):

        if not text:
            return

        self.voice.Speak(
            text
        )


    def stop(self):

        self.voice = None

        pythoncom.CoUninitialize()


speaker = None


def speak(
    text
):

    global speaker

    if speaker is None:

        speaker = Speaker()

    speaker.speak(
        text
    )
