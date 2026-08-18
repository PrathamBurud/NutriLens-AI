# 🥗 NutriLens AI

### AI-Powered Food Nutrition & Dietary Health Analyzer

NutriLens AI is an intelligent computer vision web application designed to identify meal components from images and calculate detailed nutritional values, including Calories, Macronutrients, Dietary Fiber, and Calorie Distribution percentages.

---

## 📌 Project Overview

NutriLens AI utilizes deep learning vision models and clinical nutrition databases to estimate the nutritional profile of a meal directly from a photograph. Users can either upload a food photo or capture one in real-time via their device camera.

---

## 🌟 Key Features

- **Food Recognition**: Automatically identifies individual food items, side dishes, and condiments from meal images.
- **Macronutrient Breakdown**:
  - Total Calories (kcal)
  - Protein (g)
  - Healthy Fats (g)
  - Carbohydrates (g)
  - Dietary Fiber (g)
- **Calorie Ratio Distribution**: Computes and visually represents the percentage of calories derived from Protein, Carbs, and Fats.
- **Dietary Insights**: Generates dietary tags (e.g., *Complex Carbs*, *High Protein*, *Vegetarian*) and personalized dietitian recommendations.
- **Multi-Modal Input**: Upload images (JPG, PNG, WEBP) or capture directly using the built-in camera scanner.
- **Report Generation**: One-click printable nutritional summary report.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Computer Vision & AI**: Multimodal Vision Engine
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), WebRTC
- **Deployment**: Production WSGI Ready

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/prathamburud09-design/nutrition-detection-app.git
cd nutrition-detection-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.

---

## 📁 Project Structure

```text
nutrition-detection-app/
├── app.py                # Main Flask application & routes
├── utils/
│   └── ai_service.py     # AI vision processing & nutrition parser
├── templates/
│   ├── index.html        # Upload & scanner interface
│   └── result.html       # Nutritional report & insights dashboard
├── static/
│   ├── css/style.css     # UI styles & responsive design
│   ├── js/script.js      # Client-side camera & upload interactions
│   └── uploads/          # Temporary image storage
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

---

## 👨‍💻 Author
**Pratham Burud**
