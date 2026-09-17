from faster_whisper import WhisperModel
import speech_recognition as sr
import tempfile
import os
import audioop
import time


class VoiceInput:

    def __init__(self):

        print(
            "\nLoading Whisper Small speech model..."
        )

        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 300

        self.recognizer.dynamic_energy_threshold = True

        self.recognizer.dynamic_energy_adjustment_damping = 0.15

        self.recognizer.dynamic_energy_ratio = 1.5

        self.recognizer.pause_threshold = 0.8

        self.recognizer.phrase_threshold = 0.3

        self.recognizer.non_speaking_duration = 0.5

        self.recognizer.operation_timeout = None

        self.microphone = sr.Microphone()

        print(
            "Preparing microphone..."
        )

        with self.microphone as source:

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=2
            )

        print(
            f"Microphone energy threshold: "
            f"{self.recognizer.energy_threshold:.0f}"
        )

        print(
            "Microphone ready."
        )

        print(
            "Whisper Small ready."
        )


    def check_audio_level(
        self,
        audio
    ):

        try:

            raw_data = (
                audio.get_raw_data()
            )

            if not raw_data:

                return 0

            level = audioop.rms(
                raw_data,
                2
            )

            return level

        except Exception:

            return 0


    def transcribe(
        self,
        audio_path
    ):

        try:

            segments, info = (
                self.model.transcribe(
                    audio_path,
                    language="en",
                    beam_size=5,
                    best_of=5,
                    temperature=0.0,
                    vad_filter=True,
                    vad_parameters={
                        "min_silence_duration_ms": 500,
                        "speech_pad_ms": 200
                    }
                )
            )

            text_parts = []

            for segment in segments:

                text = (
                    segment.text.strip()
                )

                if text:

                    text_parts.append(
                        text
                    )

            final_text = (
                " ".join(
                    text_parts
                ).strip()
            )

            return final_text

        except Exception as error:

            print(
                f"\nWhisper error: "
                f"{error}"
            )

            return ""


    def listen(
        self
    ):

        audio_path = None

        try:

            with self.microphone as source:

                print(
                    "\nLISTENING...",
                    end=" ",
                    flush=True
                )

                audio = (
                    self.recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=7
                    )
                )

            audio_level = (
                self.check_audio_level(
                    audio
                )
            )

            if audio_level < 100:

                print(
                    "\nAudio too quiet."
                )

                return None

            print(
                "processing..."
            )

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as file:

                audio_data = (
                    audio.get_wav_data(
                        convert_rate=16000,
                        convert_width=2
                    )
                )

                file.write(
                    audio_data
                )

                audio_path = (
                    file.name
                )

            start_time = time.time()

            text = (
                self.transcribe(
                    audio_path
                )
            )

            processing_time = (
                time.time() -
                start_time
            )

            if not text:

                print(
                    "No understandable "
                    "speech detected."
                )

                return None

            text = (
                text.lower()
                .strip()
            )

            print(
                f"\rYOU: {text}"
            )

            print(
                f"Speech processed in "
                f"{processing_time:.2f}s"
            )

            return text

        except sr.WaitTimeoutError:

            return None

        except Exception as error:

            print(
                f"\nVOICE ERROR: "
                f"{error}"
            )

            return None

        finally:

            if (
                audio_path is not None
                and
                os.path.exists(
                    audio_path
                )
            ):

                try:

                    os.remove(
                        audio_path
                    )

                except Exception:

                    pass
