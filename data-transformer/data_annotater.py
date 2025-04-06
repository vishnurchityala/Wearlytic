import requests
import google.generativeai as genai

genai.configure(api_key="")

gen_model = genai.GenerativeModel('gemini-2.0-flash')


def get_dominant_color(image_url, initial_tag=""):
    print("Fetching dominant color...")
    try:
        print(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img_data = response.content
        print("Image downloaded successfully.")

        prompt_text = "What is the dominant color of this image?"
        if initial_tag:
            prompt_text = f"What is the dominant color of the {initial_tag} in this image? Provide the answer as an RGB tuple and a descriptive color name. Give response in format: (255, 255, 255)white"

        print("Sending request to Gemini AI model...")
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
        print(f"Received response: {color_text}")

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
                    print("Successfully extracted dominant color.")
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
    print("Fetching image tags...")
    try:
        print(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img_data = response.content
        print("Image downloaded successfully.")

        prompt_text = f"Analyze this image and provide detailed descriptive tags. The primary object/concept is '{initial_tag}'. Provide tags in a comma-separated format. Ensure at least 15 tags are provided. Keep the tags in such way that it can be used in data analysis for clustering and predictions. Do not include any text before or after the comma-separated list."

        print("Sending request to Gemini AI model for tags...")
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
        print(f"Received tags: {tag_text}")

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


image_url = "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/26817180/2024/1/7/d60ae622-4081-47b9-8064-71c965ad1ff31704614054373ATHLISISWomenBlackLightweightTrainingorGymSportyJacket1.jpg"
initial_tag = "Jacket"

print("Starting image analysis...")
dominant_color = get_dominant_color(image_url, initial_tag)  # Pass the initial tag
tags = get_image_tags(image_url, initial_tag)

print("Processing results...")
if dominant_color:
    color_code, color_name = dominant_color
    print(f"Dominant Color: {color_code}, {color_name}")
else:
    print("Dominant Color: None")
print(f"Tags: {tags}")
print("Process completed.")
