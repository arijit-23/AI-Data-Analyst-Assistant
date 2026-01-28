# 🤖 AI-Data-Analyst-Assistant

An end-to-end, AI-powered web application that transforms raw, messy data into actionable insights. Built with **Streamlit**, **Pandas**, and **OpenAI**.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458.svg)

---

## 🌟 Key Features

* **🧹 Auto-Cleaning:** One-click removal of duplicates, trimming whitespace, fixing date formats, and intelligent missing-value imputation.
* **📈 Smart Visuals:** Automatically detects numeric metrics and categorical data to generate distributions, top-category charts, and time-series trends.
* **🤖 AI Chatbot:** A dedicated "Chat with Data" interface. Features a **Demo Mode** that uses local dataset statistics even if you don't have an API key.
* [cite_start]**⚙️ Dual Insight Modes:** Toggle between **Auto-Insights** (AI-driven) and **Manual Charts** for custom control.

---

## 🏗️ Project Architecture

The project is designed with a modular structure to ensure scalability:

> **User** > └── **Streamlit UI** (`app.py`)
>     ├── **Data Cleaning Logic** (`utils.py`)
>     ├── **Insights & Charts** (`utils.py`)
>     └── **Chatbot** (`chatbot.py`)
>         ├── Demo Mode (Offline)
>         └── Live AI (Optional)
### File Breakdown:
| File | Responsibility |
| :--- | :--- |
| **`app.py`** | The main entry point. [cite_start]Manages page navigation, session state, and the file upload UI. |
| **`utils.py`** | The "Heavy Lifter." Contains logic for auto-cleaning data and calculating complex aggregates. |
| **`chatbot.py`** | Manages conversation history and determines whether to use Live AI or the local Demo engine. |
| **`requirements.txt`** | Lists necessary libraries: `streamlit`, `pandas`, `numpy`, and `openai`. |

---

## 💡 Core Idea of This Project
In real-world data analyst roles, data comes messy, and stakeholders want fast insights. This app proves that:
* **Automation:** A data analyst can automate the full workflow.
* **Accessibility:** Stakeholders can ask questions in plain English.
* **Reliability:** The app includes a "Demo Mode" that works even without API credits.

**The Workflow:**
`Upload` → `Clean` → `Analyze` → `Visualize` → `Ask questions in plain English`

---
---

## 🧠 Application Logic (`app.py`)
`app.py` is the brain of the application. It manages:
* **Navigation:** Sidebar and page switching.
* **File Management:** Handling CSV/Excel uploads.
* **State Management:** Storing cleaned data for use in the chatbot.

  ---

---

## ⚙️ 1. Installation
Clone the repository and prepare your Python environment:

```bash
git clone [https://github.com/your-username/AI-Data-Analyst-Assistant.git](https://github.com/your-username/AI-Data-Analyst-Assistant.git)
cd AI-Data-Analyst-Assistant
pip install -r requirements.txt

```
---

## 🔑 2. Environment Setup
The app uses OpenAI for advanced reasoning. Add your key to your environment variables to enable "Live Mode":
```bash
export OPENAI_API_KEY='your-key-here'
```
For Windows (Command Prompt):

```bash
set OPENAI_API_KEY=your-key-here
```
💡 Note: If you don't provide a key, the app will automatically switch to Demo Mode, which uses local Pandas logic to answer your questions.


## 🚀 3. Run the App
Once your environment is set up, launch the Streamlit server:
```bash
streamlit run app.py
```

## 🛠️ How it Works (The Logic)
The Cleaning Pipeline
The clean_dataframe function in utils.py ensures your data is "analysis-ready" through these steps:

Normalization: Trims whitespace from column names and text.

Date Detection: Automatically converts date-like columns if a 60% match is found.

Imputation: Fills numeric gaps with the median and text gaps with the mode.

The Intelligent Chatbot
The chatbot in chatbot.py features a robust fallback system:

Live AI: Attempts to use gpt-4o-mini for complex data reasoning.

Offline Logic: If the API fails, it uses pre-written Pandas scripts to give you accurate summaries of your data trends and missing values.

## 📊 Sample Visuals
The app is built to be "data-aware." It automatically detects key metrics like Sales, Revenue, or Profit to build your dashboard instantly without manual configuration.

https://github.com/arijit-23/AI-Data-Analyst-Assistant/commit/d21e7dd316b2ac3379fbae2d5c46aa601c417167


