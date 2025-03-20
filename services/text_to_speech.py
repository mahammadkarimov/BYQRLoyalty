from gtts import gTTS


def generate_audio(text, language, output_path):
    """
    Converts text to speech and saves it as an audio file.

    Parameters:
    - text (str): The text to convert into audio.
    - language (str): The language code (e.g., 'en' for English, 'az' for Azerbaijani).
    - output_path (str): The path where the audio file will be saved.

    Returns:
    - str: The path to the generated audio file.
    """

    tts = gTTS(text=text, lang=language)


    tts.save(output_path)

    return output_path




