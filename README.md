# AI-Data-Analyst-Assistant
This repository contains a complete end-to-end AI-assisted data analysis web application built using Streamlit (Python).  The project demonstrates:  How a data analyst approaches raw data  How to clean, analyze, visualize, and explain data. How to design an AI chatbot that works even without API credits.

Core Idea of This Project
The real-world problem
In real data analyst roles:
Data comes messy
Stakeholders want fast insights
Not everyone understands SQL or charts
AI tools often fail when API credits run out
What this project proves
This app shows that:
A data analyst can automate the full workflow
AI can be used responsibly and safely
A project can still work offline (demo mode)
💡 Upload → Clean → Analyze → Visualize → Ask questions in plain English

Architecture :
User
 │
 ▼
Streamlit UI (app.py)
 │
 ├── Data Cleaning Logic (utils.py)
 ├── Insights & Charts (utils.py)
 └── Chatbot (chatbot.py)
        ├── Demo Mode (offline)
        └── Live AI (optional)

File Structure :
app.py                  → Main Streamlit app (UI + flow control)
utils.py                → Data cleaning & analysis functions
chatbot.py              → AI chatbot (demo + optional live AI)
requirements.txt        → Python dependencies
tempCodeRunnerFile.py   → Local test file (not required for app)

app.py — Main Application (UI + Logic)
Concept

app.py is the brain of the application.
It controls:
• Navigation
• File upload
• Page switching
• Interaction between cleaning, insights, and chatbot

1️ > Page Configuration:
st.set_page_config(page_title="AI Data Analyst Assistant", layout="wide")

