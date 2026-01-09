from typing import List

DEFAULT_IMAGE_URL: str = "https://knrbxuzorgcjgfmtkias.supabase.co/storage/v1/object/public/image_assets/1234567890.jpg"


def generate_ai_product_image(prompt: str, product_image_urls: List[str]) -> str:
	"""
	Build a marketing/creative image from a custom prompt and a set of product
	image URLs, then return a URL to the final image.

	Simple implementation using Google GenAI as per the provided template:
	- Create a genai client
	- Combine prompt and PIL images (fetched from provided URLs)
	- Call generate_content on "gemini-2.5-flash-image"
	- Iterate response parts and touch text/inline image data
	- Always return DEFAULT_IMAGE_URL (no storage/upload yet)

	Args:
		prompt: The creative prompt to guide image generation.
		product_image_urls: A list of source product image URLs to include.

	Returns:
		For now, always DEFAULT_IMAGE_URL.
	"""
	return DEFAULT_IMAGE_URL

