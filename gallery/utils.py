import base64
from PIL import Image
import io
from django.conf import settings
import openai
import spacy

# Initialize the OpenAI client
openai.api_key = settings.OPENAI_API_KEY
client = openai.OpenAI(api_key=openai.api_key)

# Load SpaCy for NLP tasks
nlp = spacy.load("en_core_web_sm")

def extract_tags(description):
    """
    Extracts nouns and adjectives as tags from the description.
    """
    doc = nlp(description)
    tags = {token.lemma_ for token in doc if token.pos_ in ["NOUN", "ADJ"]}
    return list(tags)

def resize_image(image_path, max_size=(512, 512)):
    with Image.open(image_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.thumbnail(max_size)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def analyze_image_with_openai(image_path):
    """
    Analyzes the image using OpenAI's gpt-4o-mini model via streaming API.
    """
    base64_image = resize_image(image_path)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}}
                ]}
            ],
            max_tokens=150
        )

        result_description = response.choices[0].message.content
        if result_description:
            tags = extract_tags(result_description)
            return {"tags": tags, "status": "success"}
        else:
            return {"status": "error", "message": "No valid response from OpenAI."}
    except openai.APIError as e:
        return {"status": "error", "message": f"OpenAI API error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}