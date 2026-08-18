"""
=============================================================================
NutriLens AI - AI Vision & Nutrition Estimation Service
=============================================================================
This module handles:
1. Multimodal neural vision processing for meal images.
2. Clinical Dietitian prompting for high macronutrient and micronutrient accuracy.
3. Complete Macro Extraction: Calories, Protein, Fat, Carbs, Dietary Fiber, and Health Insights.
4. In-memory caching for zero latency on duplicate scans.
5. Safe Error Masking: Ensures clean, professional output with zero raw technical leakage.
=============================================================================
"""

import sys
import os
import json
import base64
import hashlib
import re
import io
import requests
from PIL import Image
from dotenv import load_dotenv
from groq import Groq

# Ensure UTF-8 console output on Windows/Linux/macOS
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# In-memory cache for duplicate image requests: { cache_key: analysis_data }
_IMAGE_CACHE = {}


def get_groq_client():
    """
    Initializes and returns the AI client if key is present.
    """
    load_dotenv(override=True)
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)


def optimize_and_encode_image(image_path, max_dimension=384):
    """
    Resizes and compresses the image to optimize processing speed and performance.
    Returns: (raw_bytes, base64_string, mime_type)
    """
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80, optimize=True)
            image_bytes = buffer.getvalue()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return image_bytes, base64_string, "image/jpeg"
    except Exception:
        with open(image_path, "rb") as f:
            raw_bytes = f.read()
            return raw_bytes, base64.b64encode(raw_bytes).decode('utf-8'), "image/jpeg"


def build_dietitian_prompt(food_hint=None):
    """
    Constructs an academic, clinical-grade nutrition prompt for maximum accuracy.
    """
    hint_clause = f"User Context / Hint: '{food_hint}'. Use as reference." if food_hint else ""

    system_prompt = f"""You are an Elite Clinical Dietitian and AI Nutrition Vision Specialist.
Analyze the food items visible in this image with high biochemical accuracy.
{hint_clause}

CLINICAL ACCURACY GUIDELINES:
1. DISH IDENTIFICATION: Accurately identify all distinct culinary items (e.g., 'Idli', 'Sambar', 'Coconut Chutney', 'Tomato Chutney', 'Masala Dosa', 'Paneer Tikka', 'Chapati', 'Dal', 'Grilled Chicken Salad').
2. PORTION SIZING: Estimate realistic portion sizes and weights based on standard serving dishes (e.g. 1 medium roti = 35g, 1 bowl dal = 150g, 1 dosa = 150g).
3. MACRO INTEGRITY: Accurately compute Protein, Fats, Carbs, Dietary Fiber, and Total Calories.
   Formula: Calories ≈ (Protein * 4) + (Carbs * 4) + (Fat * 9).
4. HEALTH INSIGHTS:
   - Provide 2-3 dietary tags (e.g., 'Complex Carbs', 'High Protein', 'High Fiber', 'Balanced Nutrition', 'Vegetarian').
   - Provide 1 actionable dietitian recommendation on nutritional balance and health benefits.
5. Keep internal thinking very brief (<25 words). Reply ONLY with valid JSON matching this schema:

```json
{{
  "tags": ["Complex Carbs", "Moderate Protein", "High Fiber", "Vegetarian"],
  "dietitian_tip": "Balanced meal providing sustained complex carbohydrates and dietary fiber for digestive health and sustained energy.",
  "items": [
    {{
      "name": "Food Name",
      "quantity": "Portion size (e.g. 3 pieces (150g), 1 bowl (100g))",
      "calories": 180,
      "protein": 6.0,
      "fat": 1.0,
      "carbs": 36.0,
      "fiber": 2.5
    }}
  ]
}}
```"""
    return system_prompt


def parse_nutrition_json(raw_text):
    """
    Resilient multi-stage parser to extract valid nutrition and health insights.
    """
    if not raw_text:
        return None

    # Step 1: Strip completed <think>...</think> tags
    text_clean = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()

    # Step 2: Extract from ```json ... ``` code fence
    match = re.search(r'```json\s*(.*?)\s*```', text_clean if text_clean else raw_text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
                return data
        except Exception:
            pass

    # Step 3: Parse cleaned text directly
    if text_clean:
        try:
            data = json.loads(text_clean)
            if isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
                return data
        except Exception:
            pass

    # Step 4: Find outer { ... "items" ... } block
    match = re.search(r'(\{[\s\S]*"items"[\s\S]*\})', raw_text)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
                return data
        except Exception:
            pass

    # Step 5: Fallback - Extract individual item objects with regex if list was cut off
    items = []
    item_pattern = re.findall(
        r'\{\s*"name":\s*"([^"]+)",\s*"quantity":\s*"([^"]+)",\s*"calories":\s*([0-9.]+),\s*"protein":\s*([0-9.]+),\s*"fat":\s*([0-9.]+),\s*"carbs":\s*([0-9.]+)(?:,\s*"fiber":\s*([0-9.]+))?',
        raw_text
    )
    for match_item in item_pattern:
        try:
            fiber_val = float(match_item[6]) if len(match_item) > 6 and match_item[6] else 1.0
            items.append({
                "name": match_item[0].strip(),
                "quantity": match_item[1].strip(),
                "calories": round(float(match_item[2]), 1),
                "protein": round(float(match_item[3]), 1),
                "fat": round(float(match_item[4]), 1),
                "carbs": round(float(match_item[5]), 1),
                "fiber": round(fiber_val, 1)
            })
        except Exception:
            continue

    if items:
        return {
            "tags": ["Nutritious Meal", "Balanced Nutrition"],
            "dietitian_tip": "Balanced meal with essential macronutrients and dietary fiber to support healthy digestion and energy.",
            "items": items
        }

    return None


def _run_primary_engine(base64_image, mime_type, food_hint=None):
    """
    Primary neural vision execution pipeline.
    """
    load_dotenv(override=True)
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == "your_google_api_key_here":
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    system_prompt = build_dietitian_prompt(food_hint)

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt + "\n\nAnalyze this meal and return the nutrition JSON."},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=45)
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            parsed_data = parse_nutrition_json(raw_text)
            if parsed_data and "items" in parsed_data:
                return parsed_data
    except Exception:
        pass

    return None


def _run_secondary_engine(base64_image, food_hint=None):
    """
    Secondary neural vision execution pipeline.
    """
    client = get_groq_client()
    if not client:
        return None

    system_prompt = build_dietitian_prompt(food_hint)

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the food image and output the nutrition JSON."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="qwen/qwen3.6-27b",
            temperature=0.0,
            max_tokens=450
        )
        raw_output = response.choices[0].message.content.strip()
        parsed_data = parse_nutrition_json(raw_output)
        if parsed_data and "items" in parsed_data:
            return parsed_data
    except Exception:
        pass

    return None


def analyze_food_image(image_path, food_hint=None):
    """
    Main orchestrator: Executes AI Vision Nutrition Analysis with automated failover.
    
    Returns:
        tuple: (data_dict, user_friendly_error_message)
    """
    print(f"🤖 NutriLens Vision: Processing image...")

    # 1. Compress and encode image
    image_bytes, base64_image, mime_type = optimize_and_encode_image(image_path, max_dimension=384)

    # 2. Check in-memory cache to save compute
    cache_key = hashlib.md5(image_bytes).hexdigest()
    if food_hint:
        cache_key += f"_{food_hint.strip().lower()}"

    if cache_key in _IMAGE_CACHE:
        print("⚡ Returning cached nutrition analysis.")
        return _IMAGE_CACHE[cache_key], None

    # 3. Pipeline 1: Primary Vision Analysis
    primary_data = _run_primary_engine(base64_image, mime_type, food_hint)
    if primary_data and "items" in primary_data and len(primary_data["items"]) > 0:
        _IMAGE_CACHE[cache_key] = primary_data
        print(f"✅ Successfully identified {len(primary_data['items'])} food item(s).")
        return primary_data, None

    # 4. Pipeline 2: Secondary Vision Analysis (Failover)
    secondary_data = _run_secondary_engine(base64_image, food_hint)
    if secondary_data and "items" in secondary_data and len(secondary_data["items"]) > 0:
        _IMAGE_CACHE[cache_key] = secondary_data
        print(f"✅ Successfully identified {len(secondary_data['items'])} food item(s).")
        return secondary_data, None

    # 5. Safe, clean fallback message
    print("⚠️ Unable to identify food components from image.")
    return None, "Unable to analyze food in this photo. Please ensure the image is clear and well-lit, or add a food hint."
