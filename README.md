# 🥗 NutriLens AI — AI-Powered Food Nutrition & Dietary Analyzer

NutriLens AI is an intelligent computer vision application that analyzes meal images and delivers clinical-grade nutritional breakdowns including Calories, Macronutrients (Protein, Fats, Carbohydrates), Dietary Fiber, Physiological Calorie Distribution, and Dietitian Health Insights.

---

## ✨ Key Features

- 📸 **Multi-Modal Meal Input**: Supports instant drag-and-drop file upload or live camera capture via WebRTC.
- ⚡ **Dual AI Vision Engine**: Powered by **Google Gemini 2.5 Flash Vision** with automatic failover to **Groq Vision AI (`qwen/qwen3.6-27b`)** for 100% uptime and high accuracy.
- 🔬 **Comprehensive Macro Breakdown**:
  - **Total Calories (kcal)**
  - **Protein (g)**
  - **Healthy Fats (g)**
  - **Carbohydrates (g)**
  - **Dietary Fiber (g)**
- 📊 **Physiological Calorie Distribution**: Dynamic macro percentage visualization based on Atwater physiological energy factors ($4\text{ kcal/g for Protein \& Carbs, } 9\text{ kcal/g for Fats}$).
- 🥗 **Dietitian Verdict & Health Guidance**: Automatically generates dietary tags and actionable nutritional advice tailored to the scanned meal.
- 🖨️ **Export & Print**: One-click nutrition summary report generation.
- 🛡️ **Fault-Tolerant & Safe**: In-memory caching, client-side image compression, and graceful error handling.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask
- **AI Vision Models**: Google Gemini 2.5 Flash / Groq Vision (`qwen/qwen3.6-27b`)
- **Image Processing**: Pillow (PIL)
- **Frontend**: Modern Vanilla HTML5, CSS3 (Glassmorphism & CSS Custom Properties), JavaScript (ES6+), WebRTC API
- **Deployment**: Render / Railway ready (`Procfile`, `render.yaml`)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/prathamburud09-design/nutrition-detection-app.git
cd nutrition-detection-app
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```
> *Get a free Google Gemini key at [Google AI Studio](https://aistudio.google.com/app/apikey) and a free Groq key at [Groq Console](https://console.groq.com).*

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📁 Project Architecture

```text
nutrition-detection-app/
├── app.py                # Flask controller, routing & macro calculations
├── utils/
│   └── ai_service.py     # Dual-provider AI vision orchestrator & JSON parser
├── static/
│   ├── css/style.css     # Design system & responsive styles
│   ├── js/script.js      # Camera capture, drag-drop & toast notifications
│   └── uploads/          # Temporary upload directory (.gitignored)
├── templates/
│   ├── index.html        # Scanner & upload user interface
│   └── result.html       # Nutritional report & dietitian insights dashboard
├── requirements.txt      # Python dependencies
├── Procfile              # Production WSGI process definition
├── render.yaml           # Cloud deployment configuration
└── README.md             # Project documentation
```

---

## 👨‍💻 Author
**Pratham Burud**
