import os
import json
import base64
import hashlib
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def configure_ai():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == "your_groq_api_key_here":
        print("❌ GROQ_API_KEY not found or invalid in environment variables")
        return None
    
    return Groq(api_key=api_key)

# In-memory cache for identical images
_IMAGE_CACHE = {}

def analyze_food_image(image_path, food_hint=None):
    """
    Analyze food image using Groq API
    Returns a list of detected food items with nutrition info
    """
    print(f"🤖 AI Service: Analyzing {image_path} with Groq")
    
    client = configure_ai()
    if not client:
        return None

    try:
        # Encode the image
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
        # Check cache for exact same image
        cache_key = hashlib.md5(image_bytes).hexdigest()
        if food_hint:
            cache_key += f"_{food_hint}"
            
        if cache_key in _IMAGE_CACHE:
            print("🤖 AI Service: Returning exactly identical cached result for the same image")
            return _IMAGE_CACHE[cache_key]
        
        hint_instruction = f"IMPORTANT: The user has identified this context/food as: '{food_hint}'. Trust this hint to explicitly identify the primary food, then deduce calories and macros accurately." if food_hint else "Carefully distinguish between visually similar Indian dishes (e.g., Rice, Poha, Upma) based strictly on texture."
        
        system_prompt = (
            "You are an Elite Dietitian and Culinary Expert. Analyze the food in this image with high precision.\n"
            f"{hint_instruction}\n"
            "CRITICAL RULES FOR ACCURACY:\n"
            "1. IDENTIFICATION: Identify exact authentic names (e.g., 'Roti' instead of 'Flatbread').\n"
            "2. PORTION SIZING: Be extremely realistic about portion sizes based on the visual scale relative to the plate. DO NOT overestimate.\n"
            "   - A standard Roti/Chapati is ~30g-40g.\n"
            "   - Small side portions (like sprouts, chana, or dal on a plate) are usually 50g-80g max.\n"
            "3. NUTRITIONAL ACCURACY: Calories and macros MUST strictly match standard nutritional databases for the estimated quantity.\n"
            "   - E.g., 1 medium Roti (40g) is ~110-120 kcal. Do not inflate this.\n"
            "   - Ensure macronutrient math is logical (Protein*4 + Carbs*4 + Fat*9 ≈ Calories).\n\n"
            "You MUST reply in pure JSON format strictly matching this schema:\n"
            "{\n"
            '    "items": [\n'
            "        {\n"
            '            "name": "Exact Food Name",\n'
            '            "reasoning": "Step-by-step reasoning for portion size and macros based on visual evidence.",\n'
            '            "quantity": "Estimated quantity (e.g. 1 medium (40g), 1/2 katori (70g))",\n'
            '            "calories": 110,\n'
            '            "protein": 3.5,\n'
            '            "fat": 1.0,\n'
            '            "carbs": 22.0\n'
            "        }\n"
            "    ]\n"
            "}"
        )
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the food in this image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"},
            temperature=0.0,
            seed=42
        )
        
        # Clean up response text
        text = chat_completion.choices[0].message.content.strip()
        print(f"🤖 AI Raw Response Length: {len(text)} chars")
        
        # Extract JSON
        try:
            parsed_json = json.loads(text)
            results = parsed_json.get("items", [])
            # Save to cache
            _IMAGE_CACHE[cache_key] = results
            return results
        except Exception as e:
            print(f"❌ AI did not return a valid JSON object: {e}")
            return None
        
    except Exception as e:
        print(f"❌ AI Analysis Error: {e}")
        return None
