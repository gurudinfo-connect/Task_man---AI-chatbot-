# Task_man - AI-chatbot
Task_Man🤖 is an AI-powered LLM chatbot designed to automate task management, answer queries, and provide intelligent assistance. Built with FastAPI, RAG, vector databases, and modern AI workflows, it delivers context-aware, accurate, and efficient responses in real time.

🚀 Task_Man – AI-Powered Task Management Assistant

Task_Man is an intelligent productivity web application built with Flask, SQLite, JavaScript, and OpenAI API. It combines task management and conversational AI into a single platform, allowing users to manage tasks, track productivity, and interact with an AI assistant.

✨ Features
🔐 Authentication System
User Registration
Secure Login & Logout
Password Hashing
Session Management
🤖 AI Chat Assistant
Create and manage chat sessions
Context-aware conversations
OpenAI API Integration
Export chat history
Delete chat conversations
✅ Task Management
Create Tasks
Update Task Status
Mark Tasks as Completed
Set Priorities
Due Date Management
Delete Tasks
Filter Tasks
📊 Dashboard Analytics
Task Statistics
Completed vs Pending Tasks
Recent Activities
Weekly Productivity Tracking
👤 User Profile
Update Profile Information
Change Password
Personalized User Dashboard
⚙️ Settings Page
Application Preferences
User Configuration Options
🏗️ Project Structure
Task_Man/
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── chat.html
│   ├── tasks.html
│   ├── profile.html
│   └── settings.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── landing.css
│   │   ├── dashboard.css
│   │   ├── chat.css
│   │   ├── tasks.css
│   │   └── ...
│   │
│   ├── js/
│   │   ├── main.js
│   │   ├── chat.js
│   │   ├── dashboard.js
│   │   └── ...
│   │
│   └── images/
│
├── instance/
│   └── taskman.db
│
├── .env
├── requirements.txt
├── README.md
└── .gitignore
🛠️ Tech Stack
Backend
Python
Flask
Flask-SQLAlchemy
Flask-Login
SQLite
Frontend
HTML5
CSS3
JavaScript
Jinja2 Templates
AI Integration
OpenAI API
GPT Models
⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/yourusername/task_man.git
cd task_man
2️⃣ Create Virtual Environment
python -m venv venv

Activate Environment

Windows

venv\Scripts\activate

Linux/Mac

source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
5️⃣ Run Application
python app.py

Server starts at:

http://127.0.0.1:5000
📋 Required Packages
Flask
Flask-SQLAlchemy
Flask-Login
python-dotenv
openai
Werkzeug

Install manually:

pip install Flask Flask-SQLAlchemy Flask-Login python-dotenv openai Werkzeug
🤖 AI Commands Supported

Users can interact with Task_Man using natural language:

add task: Complete portfolio
create task: Learn Flask
list my tasks
complete task: Learn Flask
help
📈 Dashboard Metrics
Total Tasks
Completed Tasks
Pending Tasks
Daily Productivity
Weekly Activity Tracking
🔒 Security Features
Password Hashing
Session Authentication
Protected Routes
User-Specific Data Access
Secure Login System
🎯 Future Enhancements
Voice Assistant Integration
Email Notifications
Google Calendar Sync
Task Reminders
Dark Mode
Team Collaboration
AI Productivity Insights
Mobile Application
👨‍💻 Author

Guru Somasekhar D

Skills
Python
Flask
Generative AI
Large Language Models (LLMs)
Prompt Engineering
HTML/CSS/JavaScript
SQL
⭐ Contributing

Contributions are welcome!

Fork the repository
Create a feature branch
Commit your changes
Push to your branch
Create a Pull Request
📄 License

This project is licensed under the MIT License.

🌟 If you like this project, don't forget to star the repository! ⭐
git add .
git commit -m "Initial commit - Task_Man AI Assistant"
git push origin main
