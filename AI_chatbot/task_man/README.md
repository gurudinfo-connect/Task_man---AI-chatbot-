# 🤖 Task_Man — Intelligent AI Task Assistant

A full-stack AI productivity app built with **Flask** + **SQLite** featuring a beautiful dark glassmorphism UI.

## ✨ Features

- 🧠 **AI Chat** — Conversational assistant (smart fallback + optional OpenAI GPT integration)
- ✅ **Task Manager** — Full CRUD with priorities, statuses, due dates
- 📊 **Dashboard** — Weekly activity charts, stats, today's schedule
- 💬 **Chat History** — Persistent sessions with search and export
- 👤 **User Auth** — Register, login, profile settings, password change
- 🎨 **Dark glassmorphism UI** — Responsive, mobile-friendly, smooth animations

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment (optional)
```bash
cp .env.example .env
# Edit .env and add your OpenAI key for full AI responses
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
Visit **http://localhost:5000**

## 🔑 Demo Account
- **Email:** `demo@taskman.ai`
- **Password:** `demo1234`

## 📁 Project Structure
```
taskman/
├── app.py              # Flask backend + API + AI engine
├── requirements.txt    # Python dependencies
├── .env.example        # Environment config template
├── templates/
│   ├── base.html       # Shared layout (sidebar, topbar, toast)
│   ├── landing.html    # Public landing page
│   ├── auth.html       # Login + register
│   ├── dashboard.html  # Stats + charts
│   ├── chat.html       # AI chat interface
│   ├── tasks.html      # Task manager
│   └── profile.html    # User profile + settings
└── instance/
    └── taskman.db      # SQLite database (auto-created)
```

## 🤖 AI Configuration

Task_Man works out of the box with a smart rule-based AI. For full GPT-powered responses:

1. Get an API key from [OpenAI](https://platform.openai.com)
2. Add to `.env`: `OPENAI_API_KEY=sk-...`
3. Restart the app

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | SQLite + SQLAlchemy |
| Auth | Flask-Login + Werkzeug |
| AI | OpenAI GPT-4o-mini (optional) |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Markdown | marked.js |
| Syntax Highlighting | highlight.js |

## 📱 Pages

1. **Landing** (`/`) — Marketing page with demo preview
2. **Auth** (`/login`, `/register`) — Authentication
3. **Dashboard** (`/dashboard`) — Stats, charts, quick actions
4. **Chat** (`/chat`) — Full AI chat with history sidebar
5. **Tasks** (`/tasks`) — Task manager with filters
6. **Profile** (`/profile`) — Settings, avatar, password, API config
