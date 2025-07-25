 from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key'
BASE_DIR = os.path.dirname(__file__)

# Data files
NEWS_FILE = os.path.join(BASE_DIR, 'news.json')
GALLERY_FILE = os.path.join(BASE_DIR, 'gallery_show.json')
TEACHERS_FILE = os.path.join(BASE_DIR, 'teachers.json')
STUDENTS_FILE = os.path.join(BASE_DIR, 'students.json')
UPLOAD_DIRS = {
    'gallery': os.path.join(BASE_DIR, 'static', 'images', 'gallery'),
    'teachers': os.path.join(BASE_DIR, 'static', 'images', 'teachers'),
    'students': os.path.join(BASE_DIR, 'static', 'images', 'students')
}
ADMIN_PASSWORD = 's118044'

# Ensure JSON files and upload directories exist
for path in [NEWS_FILE, GALLERY_FILE, TEACHERS_FILE, STUDENTS_FILE]:
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f)
for directory in UPLOAD_DIRS.values():
    os.makedirs(directory, exist_ok=True)

# Helpers
def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is empty or missing, initialize with empty list
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Authentication
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped

# Public Routes
@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/news')
def news():
    items = sorted(load_json(NEWS_FILE), key=lambda x: x['timestamp'], reverse=True)
    return render_template('news.html', news_items=items)

@app.route('/gallery')
def gallery():
    items = sorted(load_json(GALLERY_FILE), key=lambda x: x['timestamp'], reverse=True)
    return render_template('gallery.html', gallery_items=items)

@app.route('/teachers')
def teachers():
    items = load_json(TEACHERS_FILE)
    return render_template('teachers.html', teacher_items=items)

@app.route('/students')
def students():
    items = load_json(STUDENTS_FILE)
    return render_template('students.html', student_items=items)

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('base_admin'))
        flash('Invalid password.', 'error')
    return render_template('login.html')

# Base Admin Dashboard
@app.route('/admin')
@admin_required
def base_admin():
    return render_template('base_admin.html')

# Generic CRUD factory
def admin_crud(json_file, upload_dir=None, template_name=None):
    # Determine template
    tpl = template_name or f"{os.path.splitext(os.path.basename(json_file))[0]}_admin.html"

    def view():
        items = load_json(json_file)
        last = items[0] if items else None
        return render_template(tpl, last=last)

    def action():
        items = load_json(json_file)
        last = items[0] if items else None
        if request.form.get('password') != ADMIN_PASSWORD:
            flash('Invalid password.', 'error')
            return redirect(request.path)

        act = request.form.get('action')
        # Delete last
        if act == 'delete' and last:
            if upload_dir:
                try:
                    os.remove(os.path.join(upload_dir, last.get('filename', '')))
                except OSError:
                    pass
            items.pop(0)
            save_json(json_file, items)
            flash('Deleted last item.', 'success')
            return redirect(request.path)

        # Post new
        if act == 'post':
            title = request.form.get('title', '').strip()
            desc = request.form.get('description', '').strip()
            if not title or not desc:
                flash('All fields are required.', 'error')
                return redirect(request.path)

            new_item = {'timestamp': datetime.utcnow().isoformat(), 'title': title, 'description': desc}
            if upload_dir and 'photo' in request.files:
                file = request.files['photo']
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_dir, filename))
                new_item['filename'] = filename

            items.insert(0, new_item)
            save_json(json_file, items)
            flash('New item added!', 'success')
            return redirect(request.path)

    return view, action

# Register CRUD routes
# News
news_view, news_action = admin_crud(NEWS_FILE, template_name='news_admin.html')
app.add_url_rule('/admin/news', 'news_admin', admin_required(news_view), methods=['GET'])
app.add_url_rule('/admin/news', 'news_admin_post', admin_required(news_action), methods=['POST'])

# Replace generic gallery_crud with custom handler below
# (remove the generic gallery registration lines)

# Teachers
teach_view, teach_action = admin_crud(TEACHERS_FILE, UPLOAD_DIRS['teachers'], 'teacher_admin.html')
app.add_url_rule('/admin/teachers', 'teacher_admin', admin_required(teach_view), methods=['GET'])
app.add_url_rule('/admin/teachers', 'teacher_admin_post', admin_required(teach_action), methods=['POST'])
# Students
stud_view, stud_action = admin_crud(STUDENTS_FILE, UPLOAD_DIRS['students'], 'student_admin.html')
app.add_url_rule('/admin/students', 'student_admin', admin_required(stud_view), methods=['GET'])
app.add_url_rule('/admin/students', 'student_admin_post', admin_required(stud_action), methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)