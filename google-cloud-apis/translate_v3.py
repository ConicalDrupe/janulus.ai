import os
from pprint import pprint

# Import the Google Cloud Translation library.
from google.cloud import translate_v3

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")


def translate_text(
    text: str = "YOUR_TEXT_TO_TRANSLATE",
    source_language_code: str = "en-US",
    target_language_code: str = "fr",
) -> translate_v3.TranslationServiceClient:
    """Translate Text from a Source language to a Target language.
    Args:
        text: The content to translate.
        source_language_code: The code of the source language.
        target_language_code: The code of the target language.
            Find available languages and codes here:
            https://cloud.google.com/translate/docs/languages#neural_machine_translation_model
    """

    # Initialize Translation client.
    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/global"

    mime_type = "text/plain"

    response = client.translate_text(
        contents=[text],
        parent=parent,
        mime_type=mime_type,
        source_language_code=source_language_code,
        target_language_code=target_language_code,
    )

    # Display the translation for the text.
    for translation in response.translations:
        print(f"Translated text: {translation.translated_text}")

    return response


if __name__ == "__main__":
    english_text = "Hello, how are you?"
    response = translate_text(
        text=english_text, source_language_code="en-US", target_language_code="hi"
    )

    print("\n" * 6)
    pprint(response)
