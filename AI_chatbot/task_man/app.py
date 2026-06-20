import os
import re
import random
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OpenAI and OPENAI_API_KEY) else None

app = Flask(__name__)
app.config["SECRET_KEY"] = "taskman-dev-secret-key-change-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'taskman.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_seed = db.Column(db.String(40), default="task")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chats = db.relationship("Chat", backref="user", cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship("Message", backref="chat", cascade="all, delete-orphan",
                                order_by="Message.created_at")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending")  # pending | completed
    priority = db.Column(db.String(10), default="medium")  # low | medium | high
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# Tiny rule-based assistant (placeholder for a real LLM integration)
# ---------------------------------------------------------------------------

AI_GREETINGS = [
    "On it! Here's what I found:",
    "Got it — here you go:",
    "Sure thing, let's break this down:",
]


def generate_ai_response(user_id, text, history=None):
    """Handles deterministic task commands directly; everything else is sent
    to OpenAI (if configured) for a real conversational answer."""
    history = history or [{"role": "user", "content": text}]
    lowered = text.lower().strip()

    # Task creation: "add task: Buy milk" / "create task buy milk"
    match = re.search(r"(?:add|create|new)\s+task[:\-]?\s*(.+)", lowered)
    if match:
        title = match.group(1).strip().capitalize()
        if title:
            task = Task(user_id=user_id, title=title)
            db.session.add(task)
            db.session.commit()
            return f"✅ Task created: **{title}**\n\nI've added it to your Task Manager as *pending*. Want me to set a priority or due date?"

    # Mark complete
    match = re.search(r"(?:complete|finish|done with)\s+task[:\-]?\s*(.+)", lowered)
    if match:
        keyword = match.group(1).strip()
        task = Task.query.filter(Task.user_id == user_id, Task.title.ilike(f"%{keyword}%")).first()
        if task:
            task.status = "completed"
            db.session.commit()
            return f"🎉 Marked **{task.title}** as completed. Nice work!"
        return f"I couldn't find a task matching '{keyword}'. Check your Task Manager for the exact title."

    if "list" in lowered and "task" in lowered:
        tasks = Task.query.filter_by(user_id=user_id, status="pending").all()
        if not tasks:
            return "You have no pending tasks right now. 🎉"
        lines = "\n".join(f"- {t.title} ({t.priority} priority)" for t in tasks)
        return f"Here are your pending tasks:\n\n{lines}"

    if any(g in lowered for g in ["hello", "hi", "hey"]):
        return "Hello! 👋 I'm Task_Man, your AI productivity partner. Ask me to create a task, summarize your day, or just chat about what's on your plate."

    if "remind" in lowered:
        return "⏰ Got it — I'll keep that in mind. (Tip: reminders sync with your Task Manager due dates once you set one.)"

    if "help" in lowered:
        return ("Here's what I can do:\n\n"
                "- **\"add task: <title>\"** — create a new task\n"
                "- **\"complete task: <title>\"** — mark a task done\n"
                "- **\"list my tasks\"** — see what's pending\n"
                "- Or just chat with me about your day, your goals, or anything else.")

    # Everything else goes to OpenAI for a real conversational answer
    if openai_client:
        try:
            return call_openai(history)
        except Exception as exc:
            return (f"⚠️ I couldn't reach the AI model ({exc}). "
                    "Double-check your OPENAI_API_KEY in the .env file and try again.")

    # No API key configured — fall back to a friendly notice
    greeting = random.choice(AI_GREETINGS)
    return (f"{greeting}\n\n"
            f"You said: \"{text.strip()}\"\n\n"
            "I don't have an OpenAI API key configured yet, so I can't give a real answer. "
            "Add `OPENAI_API_KEY=sk-...` to a `.env` file in this folder and restart the app to enable full AI responses.")


def call_openai(history):
    """Send the conversation history to OpenAI and return the assistant's reply."""
    system_prompt = (
        "You are Task_Man, a friendly and concise AI productivity assistant embedded "
        "in a task-management web app. Help the user with their questions, writing, "
        "code, explanations, or planning. Keep answers clear and reasonably brief. "
        "You can mention that tasks can be created by typing things like "
        "'add task: <title>' if it's relevant, but don't force it into every reply."
    )
    messages = [{"role": "system", "content": system_prompt}] + history

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=700,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Routes — Public
# ---------------------------------------------------------------------------

@app.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in every field.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Try logging in instead.", "error")
            return redirect(url_for("register"))

        user = User(name=name, email=email, avatar_seed=name[:1].upper())
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


# ---------------------------------------------------------------------------
# Routes — App (require login)
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.status == "completed"])
    pending = total - completed

    today = datetime.utcnow().date()
    todays_tasks = [t for t in tasks if t.due_date and t.due_date.date() == today]

    week_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        count = len([t for t in tasks if t.status == "completed" and t.created_at.date() == day.date()])
        week_data.append({"label": day.strftime("%a"), "count": count})

    return render_template(
        "dashboard.html",
        total=total, completed=completed, pending=pending,
        todays_tasks=todays_tasks, week_data=week_data,
        recent_tasks=sorted(tasks, key=lambda t: t.created_at, reverse=True)[:5],
    )


@app.route("/chat")
@app.route("/chat/<int:chat_id>")
@login_required
def chat_view(chat_id=None):
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).all()
    active_chat = None
    if chat_id:
        active_chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    return render_template("chat.html", chats=chats, active_chat=active_chat)


@app.route("/api/chat/new", methods=["POST"])
@login_required
def api_new_chat():
    chat = Chat(user_id=current_user.id, title="New Chat")
    db.session.add(chat)
    db.session.commit()
    return jsonify({"chat_id": chat.id})


@app.route("/api/chat/<int:chat_id>/message", methods=["POST"])
@login_required
def api_send_message(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    text = (data or {}).get("message", "").strip()
    if not text:
        return jsonify({"error": "Empty message"}), 400

    user_msg = Message(chat_id=chat.id, role="user", content=text)
    db.session.add(user_msg)

    if chat.title == "New Chat":
        chat.title = text[:40] + ("…" if len(text) > 40 else "")

    db.session.commit()

    # Build conversation history (last 20 messages) for context-aware AI replies
    recent_messages = chat.messages[-20:]
    history = [
        {"role": "user" if m.role == "user" else "assistant", "content": m.content}
        for m in recent_messages
    ]

    ai_text = generate_ai_response(current_user.id, text, history=history)
    ai_msg = Message(chat_id=chat.id, role="ai", content=ai_text)
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        "chat_title": chat.title,
        "ai_message": {
            "content": ai_msg.content,
            "timestamp": ai_msg.created_at.strftime("%I:%M %p"),
        }
    })


@app.route("/api/chat/<int:chat_id>/delete", methods=["POST"])
@login_required
def api_delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    db.session.delete(chat)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/chat/<int:chat_id>/export")
@login_required
def api_export_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    lines = [f"Task_Man Chat Export — {chat.title}", "=" * 40, ""]
    for m in chat.messages:
        speaker = "You" if m.role == "user" else "Task_Man"
        lines.append(f"[{m.created_at.strftime('%Y-%m-%d %H:%M')}] {speaker}: {m.content}")
        lines.append("")
    content = "\n".join(lines)
    from flask import Response
    return Response(content, mimetype="text/plain",
                     headers={"Content-Disposition": f"attachment;filename=chat_{chat_id}.txt"})


@app.route("/tasks")
@login_required
def tasks_view():
    status_filter = request.args.get("status", "all")
    query = Task.query.filter_by(user_id=current_user.id)
    if status_filter == "pending":
        query = query.filter_by(status="pending")
    elif status_filter == "completed":
        query = query.filter_by(status="completed")
    tasks = query.order_by(Task.created_at.desc()).all()
    return render_template("tasks.html", tasks=tasks, status_filter=status_filter)


@app.route("/api/tasks", methods=["POST"])
@login_required
def api_create_task():
    data = request.get_json()
    title = (data or {}).get("title", "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400

    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"])
        except ValueError:
            due_date = None

    task = Task(
        user_id=current_user.id,
        title=title,
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        due_date=due_date,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "title": task.title, "status": task.status, "priority": task.priority})


@app.route("/api/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def api_toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.status = "completed" if task.status == "pending" else "pending"
    db.session.commit()
    return jsonify({"id": task.id, "status": task.status})


@app.route("/api/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def api_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    current_user.name = request.form.get("name", current_user.name).strip()
    new_password = request.form.get("password", "").strip()
    if new_password:
        current_user.set_password(new_password)
    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
