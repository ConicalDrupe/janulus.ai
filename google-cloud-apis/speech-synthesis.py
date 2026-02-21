# Taken from https://docs.cloud.google.com/text-to-speech/docs/gemini-tts#before_you_begin_2

import os
import wave

from google import genai
from google.genai import types

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "global")


# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def create_audio(
    director_prompt: str,
    text: str,
    client: genai.Client,
    model_id: str = "gemini-2.5-flash-tts",
    output_language_code="en-in",
    voice_name="Kore",
):

    contents = director_prompt + text

    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=types.GenerateContentConfig(
            speech_config=types.SpeechConfig(
                language_code=output_language_code,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                ),
            ),
            temperature=2.0,
        ),
    )

    data = response.candidates[0].content.parts[0].inline_data.data
    return data


if __name__ == "__main__":

    director_prompt = ""
    hindi_text = "क्या आप को बिल्लियाँ पसंद है"
    file_name = "/home/boon/Projects/google-cloud-apis/output_speech.wav"
    client = genai.Client(vertexai=True, project=project_id, location=LOCATION)

    data = create_audio(
        director_prompt=director_prompt,
        text=hindi_text,
        client=client,
        model_id="gemini-2.5-flash-tts",
        output_language_code="hi",
        voice_name="Kore",
    )
    print(type(data))  # data is bytes!!!
    wave_file(file_name, data)  # save the file
