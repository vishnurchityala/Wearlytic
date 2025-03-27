import requests
import google.generativeai as genai

genai.configure(api_key="AIzaSyCMdaemQ6usya95fGDAsJooqxni4xexdMM")

gen_model = genai.GenerativeModel('gemini-2.0-flash')


def get_dominant_color(image_url, initial_tag=""):
    """
    Retrieves the dominant color from an image URL using Gemini, focusing
    on the color of the product described by the initial_tag.

    Args:
        image_url (str): The URL of the image.
        initial_tag (str, optional): A tag describing the product.
            Defaults to "".

    Returns:
        tuple:  ((R, G, B), color_name) or None on error.
                For example: ((255, 255, 255), "white")
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img_data = response.content

        prompt_text = "What is the dominant color of this image?"
        if initial_tag:
            prompt_text = f"What is the dominant color of the {initial_tag} in this image? Provide the answer as an RGB tuple and a descriptive color name. Give response in format: (255, 255, 255)white"

        contents = [
            {
                "parts": [
                    {"mime_type": "image/jpeg", "data": img_data},
                    {"text": prompt_text},
                ]
            }
        ]
        response = gen_model.generate_content(contents=contents)
        color_text = response.text.strip()

        try:
            start_paren = color_text.find("(")
            end_paren = color_text.find(")")
            if start_paren != -1 and end_paren != -1:
                color_tuple_str = color_text[start_paren: end_paren + 1]

                color_name_parts = color_text[end_paren + 1:].split(',')
                color_name = color_name_parts[0].split(" ")[-1].strip()

                color_tuple = eval(color_tuple_str)

                if (
                        isinstance(color_tuple, tuple)
                        and len(color_tuple) == 3
                        and all(0 <= x <= 255 for x in color_tuple)
                ):
                    return color_tuple, color_name
                else:
                    raise ValueError("Invalid color tuple format")
            else:
                raise ValueError("No color tuple found in response")
        except Exception as e:
            print(f"Error parsing color: {e}, Response was: {color_text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def get_image_tags(image_url, initial_tag=""):
    """
    Generates descriptive tags for an image using the Gemini model,
    focusing on tags related to the initial tag and formatting them
    as a comma-separated string.  Aims for consistent tag generation
    across images, optimized for data analysis.

    Args:
        image_url (str): The URL of the image.
        initial_tag (str, optional): An initial tag to guide tag generation.
            Defaults to "".

    Returns:
        str: A comma-separated string of descriptive tags, or an error message.
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img_data = response.content

        prompt_text = f"Analyze this image and provide detailed descriptive tags.  The primary object/concept is '{initial_tag}'.  Provide tags in the following comma-separated format, and adhere strictly to the categories and order: '[Primary Tag], [Secondary Tags], [Material], [Fit], [Design Details], [Pattern/Motif], [Style Era/Influence], [Intended Use], [Brand/Designer], [Target Audience], [Unique Features], [Age Group]'. Categories: - Primary Tag:  '{initial_tag}'. - Secondary Tags: Other prominent objects or concepts within the context of the primary tag (e.g., if the primary tag is 'T-shirt', secondary tags should describe parts of the T-shirt or elements on the T-shirt, not other objects in the image). - Material: Fabric type, texture (e.g., cotton, denim, soft, ribbed). - Fit: How the item fits (e.g., slim, loose, oversized). - Design Details: Specific construction elements (e.g., seams, buttons, pockets). - Pattern/Motif: Any visual patterns (e.g., floral, striped, print). - Style Era/Influence: Historical or subcultural style (e.g., vintage, modern). - Intended Use: Occasion or activity (e.g., casual, formal, activewear). - Brand/Designer: (If discernible). - Target Audience: Demographics (e.g., men, women, Gen Z, Millennials). - Unique Features: Standout characteristics of the primary tag object. - Age Group:  Likely wearer age range (e.g., children, adults). Example: 'T-shirt, Graphic print, Cotton, Oversized, Crew neck, Cartoon, Modern, Casual, Kook N Keech, Men, Mickey Mouse print, Young Adults'. Ensure at least 10 tags are provided.  Omit any category if information is not present.  Do not include any text before or after the comma-separated list."
        contents = [
            {
                "parts": [
                    {"mime_type": "image/jpeg", "data": img_data},
                    {"text": prompt_text},
                ]
            }
        ]
        response = gen_model.generate_content(contents=contents)
        tag_text = response.text.strip()

        if response and response.text:
            return tag_text
        else:
            return "No tags generated"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return None
    except Exception as e:
        print(f"Error generating tags: {e}")
        return "Error generating tags"


image_url = "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/23184604/2023/5/15/148c3339-4837-4ccd-93ee-5e9ffa072b9f1684148935778SASSAFRASWomenBlackSlimFitTrousers1.jpg"

initial_tag = "Trousers"

dominant_color = get_dominant_color(image_url, initial_tag) # Pass the initial tag
tags = get_image_tags(image_url, initial_tag)

if dominant_color:
    color_code, color_name = dominant_color
    print(f"Dominant Color: {color_code}, {color_name}")
else:
    print("Dominant Color: None")
print(f"Tags: {tags}")
