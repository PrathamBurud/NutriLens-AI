"""
=============================================================================
NutriLens AI - AI-Powered Food Nutrition & Dietary Analyzer
=============================================================================
This application handles:
1. Serving the interactive meal scanning web interface.
2. Secure validation and processing of uploaded meal images.
3. Invoking the dual-provider AI Vision Nutrition Service (Gemini / Groq).
4. Computing complete macronutrient totals (Protein, Fats, Carbs, Dietary Fiber).
5. Calculating the Calorie Distribution Split (%) based on physiological energy factors.
6. Rendering the comprehensive Clinical Nutrition & Health Insights Dashboard.
=============================================================================
"""

import sys
import os
import time
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Ensure console supports UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Import AI analysis service
from utils.ai_service import analyze_food_image

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum upload size: 16 MB

# Supported image formats
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """
    Helper function to validate allowed image extensions.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Route 1: Home Page (GET /)
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    """
    Renders the main food upload and camera scanner page.
    """
    return render_template('index.html')


# ---------------------------------------------------------------------------
# Route 2: Upload & Nutrition Analysis (POST /upload)
# ---------------------------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles image uploads, triggers AI nutrition analysis, and displays results.
    """
    print("\n" + "=" * 50)
    print("📥 Incoming Food Image for Nutritional Analysis...")
    
    try:
        # Step 1: Validate file presence
        if 'food_image' not in request.files:
            return jsonify({'error': 'Please select an image file to analyze.'}), 400
        
        file = request.files['food_image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected. Please choose a photo.'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Supported formats: JPG, PNG, WEBP, GIF, BMP.'}), 400
        
        # Step 2: Save the image securely to static/uploads/
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"💾 Image saved: {filepath}")

        # Step 3: Extract optional user context / hint
        food_hint = request.form.get('food_hint', '').strip()
        if food_hint:
            print(f"💡 User Hint: '{food_hint}'")

        # Step 4: Run AI Nutrition Analysis
        start_time = time.time()
        ai_data, error_msg = analyze_food_image(filepath, food_hint)
        processing_time = round(time.time() - start_time, 2)

        # Step 5: Check if analysis succeeded
        if error_msg or not ai_data or not ai_data.get('items'):
            user_safe_error = error_msg if error_msg else 'Unable to detect food in this image. Please upload a clearer photo.'
            return jsonify({'error': user_safe_error}), 400

        items_list = ai_data['items']
        diet_tags = ai_data.get('tags', ['Nutritious Meal', 'Balanced'])
        dietitian_tip = ai_data.get('dietitian_tip', 'Balanced meal with essential macronutrients and dietary fiber to support overall health.')

        # Step 6: Compute Aggregated Macronutrients & Dietary Fiber
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_fiber = 0
        formatted_results = []

        for item in items_list:
            cal = round(float(item.get('calories', 0)), 1)
            pro = round(float(item.get('protein', 0)), 1)
            fat = round(float(item.get('fat', 0)), 1)
            carbs = round(float(item.get('carbs', 0)), 1)
            fiber = round(float(item.get('fiber', 0.0)), 1)

            formatted_results.append({
                'food_name': item['name'],
                'quantity': item['quantity'],
                'calories': cal,
                'protein': pro,
                'fat': fat,
                'carbs': carbs,
                'fiber': fiber,
                'source': 'NutriLens AI'
            })

            total_calories += cal
            total_protein += pro
            total_fat += fat
            total_carbs += carbs
            total_fiber += fiber

        total_calories = round(total_calories, 1)
        total_protein = round(total_protein, 1)
        total_fat = round(total_fat, 1)
        total_carbs = round(total_carbs, 1)
        total_fiber = round(total_fiber, 1)

        # Step 7: Calculate Physiological Calorie Distribution (%)
        # Standard Physiological Atwater Factors: Protein = 4 kcal/g, Carbs = 4 kcal/g, Fat = 9 kcal/g
        protein_cals = total_protein * 4
        carbs_cals = total_carbs * 4
        fat_cals = total_fat * 9
        total_calc_cals = max(protein_cals + carbs_cals + fat_cals, 1.0)

        protein_pct = round((protein_cals / total_calc_cals) * 100)
        carbs_pct = round((carbs_cals / total_calc_cals) * 100)
        fat_pct = max(0, 100 - (protein_pct + carbs_pct))

        print(f"🎉 Nutrition Analysis Complete in {processing_time}s")
        print(f"📈 Total Calories: {total_calories} kcal | Protein: {total_protein}g | Carbs: {total_carbs}g | Fat: {total_fat}g | Fiber: {total_fiber}g")
        print(f"📊 Calorie Split: {protein_pct}% Protein / {carbs_pct}% Carbs / {fat_pct}% Fat")
        print("=" * 50 + "\n")

        # Step 8: Render the result dashboard template
        return render_template(
            'result.html',
            results=formatted_results,
            total_calories=total_calories,
            total_protein=total_protein,
            total_fat=total_fat,
            total_carbs=total_carbs,
            total_fiber=total_fiber,
            protein_pct=protein_pct,
            carbs_pct=carbs_pct,
            fat_pct=fat_pct,
            diet_tags=diet_tags,
            coach_tip=dietitian_tip,
            image_url=filename,
            processing_time=processing_time,
            data_sources=['NutriLens AI Vision']
        )

    except Exception as e:
        print(f"⚠️ Internal Server Note: {str(e)}")
        return jsonify({'error': 'Unable to process image at this time. Please try again with a clear photo.'}), 500


# ---------------------------------------------------------------------------
# Route 3: Server Health & Status Check (GET /debug)
# ---------------------------------------------------------------------------
@app.route('/debug')
def debug():
    """
    Health check endpoint to verify backend operational readiness.
    """
    return jsonify({
        'status': 'operational',
        'upload_folder': os.path.exists(app.config['UPLOAD_FOLDER']),
        'templates_ready': os.path.exists('templates'),
        'static_ready': os.path.exists('static')
    })


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NUTRILENS AI - FOOD NUTRITION ESTIMATOR STARTING")
    print("=" * 60)
    print(f"📁 Upload Folder : {app.config['UPLOAD_FOLDER']}")
    print("🌐 Local Server  : http://localhost:5000")
    print("=" * 60)

    # Run local Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)