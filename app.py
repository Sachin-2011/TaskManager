from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

# MongoDB - Use environment variable for production (MongoDB Atlas) or local for development
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/taskmanager")
mongo = PyMongo(app)

users = mongo.db.users
tasks = mongo.db.tasks

# ---------------- AUTH ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user'] = {'username': user['username'], '_id': str(user['_id'])}
            return redirect(url_for('tasks_page'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Username and password required', 'error')
            return render_template('signup.html')
        if users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('signup.html')
        users.insert_one({
            'username': username,
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow()
        })
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- TASKS ----------------
@app.route('/tasks')
def tasks_page():
    if 'user' not in session:
        return redirect(url_for('login'))

    filter_type = request.args.get('filter', 'all')
    query = {'user_id': session['user']['_id']}

    if filter_type == 'important':
        query['important'] = True
    elif filter_type == 'completed':
        query['completed'] = True
    elif filter_type == 'incomplete':
        query['completed'] = False

    items = list(tasks.find(query).sort('created_at', -1))
    # convert ObjectId to str for template usage
    for it in items:
        it['_id'] = str(it['_id'])
    return render_template('tasks.html', tasks=items, active_filter=filter_type, username=session['user']['username'])

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Only allow add when filter=all (frontend hides form, but backend still allows)
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if not title:
        flash('Task title is required', 'error')
        return redirect(url_for('tasks_page'))
    tasks.insert_one({
        'user_id': session['user']['_id'],
        'title': title,
        'description': description,
        'completed': False,
        'important': False,
        'created_at': datetime.utcnow()
    })
    return redirect(url_for('tasks_page'))

@app.route('/toggle_complete/<task_id>')
def toggle_complete(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id', 'error')
        return redirect(url_for('tasks_page'))
    task = tasks.find_one({'_id': oid, 'user_id': session['user']['_id']})
    if task:
        tasks.update_one({'_id': oid}, {'$set': {'completed': not task.get('completed', False)}})
    return redirect(url_for('tasks_page', filter=request.args.get('filter','all')))

@app.route('/toggle_important/<task_id>')
def toggle_important(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id', 'error')
        return redirect(url_for('tasks_page'))
    task = tasks.find_one({'_id': oid, 'user_id': session['user']['_id']})
    if task:
        tasks.update_one({'_id': oid}, {'$set': {'important': not task.get('important', False)}})
    return redirect(url_for('tasks_page', filter=request.args.get('filter','all')))

@app.route('/edit/<task_id>', methods=['POST'])
def edit_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    try:
        oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id', 'error')
        return redirect(url_for('tasks_page'))
    tasks.update_one({'_id': oid, 'user_id': session['user']['_id']}, {'$set': {'title': title, 'description': description}})
    return redirect(url_for('tasks_page', filter=request.args.get('filter','all')))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id', 'error')
        return redirect(url_for('tasks_page'))
    tasks.delete_one({'_id': oid, 'user_id': session['user']['_id']})
    return redirect(url_for('tasks_page', filter=request.args.get('filter','all')))

if __name__ == '__main__':
    # use_reloader=False avoids Windows socket issues on file changes
    app.run(debug=True, use_reloader=False)
