import commentjson
import google.generativeai as genai
import logging
import os

def do_translate_gemini(target_json, api_key, logger=None):
    """
    Translates JSON data using Google Gemini AI.

    Args:
        target_json (str): JSON data as a string to be translated.
        api_key (str): Google Gemini API key.
        logger (logging.Logger): Optional logger for logging translation status.

    Returns:
        dict: Translated JSON data.
    """
    if logger:
        logger.info("Starting translation using Gemini AI.")

    # Configure Gemini API
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        prompt = (
            "당신은 게임전문 번역가입니다. 번역하고자 하는 게임은 마인크래프트입니다.\n"
            "딕셔너리 형태의 데이터를 넘겨드릴겁니다. Key값은 그대로두고 Value값만 번역해야합니다.\n"
            "영어를 한글로 번역하는 작업이며, 답변은 Json 형태로만 주시면 됩니다.\n\n"
            f"{target_json}"
        )
        response = model.generate_content(prompt)
        
        if logger:
            logger.info("Translation request successfully sent to Gemini AI.")

        # Extract translated JSON string
        translated_json_str = response.text.strip()

        if logger:
            logger.debug(f"Raw translated response: {translated_json_str}")

        # Safely parse JSON result (assuming response is wrapped in ```json ... ```)
        # Gemini might return JSON directly, but check for code blocks
        if translated_json_str.startswith("```json"):
            translated_json_str = translated_json_str[7:-3].strip()
        elif translated_json_str.startswith("```"):
            translated_json_str = translated_json_str[3:-3].strip()

        translated_data = commentjson.loads(translated_json_str)
        if logger:
            logger.info("Translation successfully parsed into JSON format.")

        return translated_data

    except Exception as e:
        if logger:
            logger.error(f"An error occurred during translation: {e}")
        raise