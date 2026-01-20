import os
import dotenv
dotenv.load_dotenv()
from typing import List
from google import genai
from google.genai import types


def generate_ai_product_image(prompt: str,base_image: bytes,input_images: List[bytes],) -> bytes:

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    parts = [
        types.Part(text=prompt),

        types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=base_image
            )
        ),
    ]

    for img in input_images:
        parts.append(
            types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=img
                )
            )
        )

    contents = [
        types.Content(
            role="user",
            parts=parts
        )
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        ),
    )

    for candidate in response.candidates or []:
        content = candidate.content
        if not content:
            continue
        for part in content.parts or []:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data

    raise RuntimeError("No image returned by Gemini.")