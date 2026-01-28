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

> **User Interface** (`app.py`)  
> └── **Processing Engine** (`utils.py`) — *Cleaning, Stat detection, Chart aggregation* > └── **Intelligence Layer** (`chatbot.py`) — *LLM integration & Offline Demo logic*

### File Breakdown:
| File | Responsibility |
| :--- | :--- |
| **`app.py`** | The main entry point. [cite_start]Manages page navigation, session state, and the file upload UI. |
| **`utils.py`** | The "Heavy Lifter." Contains logic for auto-cleaning data and calculating complex aggregates. |
| **`chatbot.py`** | Manages conversation history and determines whether to use Live AI or the local Demo engine. |
| **`requirements.txt`** | Lists necessary libraries: `streamlit`, `pandas`, `numpy`, and `openai`. |

---

## 🚀 Getting Started

### 1. Installation
Clone this repository and install the dependencies:
```bash
git clone [https://github.com/your-username/AI-Data-Analyst-Assistant.git](https://github.com/your-username/AI-Data-Analyst-Assistant.git)
cd AI-Data-Analyst-Assistant
pip install -r requirements.txt
