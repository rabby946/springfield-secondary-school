from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.jinja_env.globals.update(enumerate=enumerate)
BASE_DIR = os.path.dirname(__file__)

# Data files
NEWS_FILE = os.path.join(BASE_DIR, 'news.json')
GALLERY_FILE = os.path.join(BASE_DIR, 'gallery_show.json')
TEACHERS_FILE = os.path.join(BASE_DIR, 'teachers.json')
MPOS_FILE = os.path.join(BASE_DIR, 'mpos.json')
COMMITTEES_FILE = os.path.join(BASE_DIR, 'committees.json')
STUDENTS_FILE = os.path.join(BASE_DIR, 'students.json')
RESULTS_FILE = os.path.join(BASE_DIR, 'results.json')
ROUTINE_FILE = os.path.join(BASE_DIR, 'routine.json')

UPLOAD_DIRS = {
    'gallery': os.path.join(BASE_DIR, 'static', 'images', 'gallery'),
    'teachers': os.path.join(BASE_DIR, 'static', 'images', 'teachers'),
    'mpos': os.path.join(BASE_DIR, 'static', 'images', 'mpos'),
    'committees': os.path.join(BASE_DIR, 'static', 'images', 'committees'),
    'students': os.path.join(BASE_DIR, 'static', 'images', 'students'), 
    'results' : os.path.join(BASE_DIR, 'static', 'files', 'results'),
    'routine' : os.path.join(BASE_DIR, 'static', 'files', 'routine')
}
ADMIN_PASSWORD = 'bongram99'
nonews = "No published news right now"
Headline = {'news' : 'No published news right now'}
# Ensure JSON files and upload directories exist
for path in [NEWS_FILE, GALLERY_FILE, TEACHERS_FILE, MPOS_FILE, STUDENTS_FILE, RESULTS_FILE, COMMITTEES_FILE]:
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
@app.route('/ping')
def ping():
    return 'pong' 

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results')
def results():
    items = load_json(RESULTS_FILE)
    return render_template('results.html', results_items=items)

@app.route('/routine')
def routine():
    items = load_json(ROUTINE_FILE)
    return render_template('routine.html', routine_items=items)

@app.route('/')
def home():
    items = sorted(load_json(NEWS_FILE), key=lambda x: x['timestamp'], reverse=True)
    Headline["news"] = items[0]['title'] if items else nonews
    return render_template('home.html', text=Headline["news"])

@app.route('/news')
def news():
    items = load_json(NEWS_FILE)
    return render_template('news.html', news_items=items)

@app.route('/gallery')
def gallery():
    items = load_json(GALLERY_FILE)
    return render_template('gallery.html', gallery_items=items)

@app.route('/teachers')
def teachers():
    items = load_json(TEACHERS_FILE)
    return render_template('teachers.html', teacher_items=items)

@app.route('/mpos')
def mpos():
    items = load_json(MPOS_FILE)
    return render_template('mpos.html', mpo_items=items)

@app.route('/committees')
def committees():
    items = load_json(COMMITTEES_FILE)
    return render_template('committees.html', committee_items=items)

@app.route('/students')
def students():
    items = load_json(STUDENTS_FILE)
    return render_template('students.html', student_items=items)

@app.route('/logout')
def logout():
    session["admin"] = False
    flash('Logged out successfully.', 'w')
    return redirect(url_for('home'))

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("admin", False):
        flash('Already logged in.', 'w')
        return redirect(url_for('base_admin'))

    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Logged in successfully.', 'w')
            return redirect(url_for('base_admin'))
        flash('Invalid password.', 'error')
        
    return render_template('login.html')

# News detail
@app.route('/news/<int:idx>')
def news_detail(idx):
    items = load_json(NEWS_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('news'))
    return render_template('news_detail.html', item=items[idx])

# Gallery detail
@app.route('/gallery/<int:idx>')
def gallery_detail(idx):
    items = load_json(GALLERY_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('gallery'))
    return render_template('gallery_detail.html', item=items[idx])

@app.route('/teachers/<int:idx>')
def teacher_detail(idx):
    items = load_json(TEACHERS_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('teachers'))
    return render_template('teacher_detail.html', teacher=items[idx])

@app.route('/mpos/<int:idx>')
def mpo_detail(idx):
    items = load_json(MPOS_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('mpos'))
    return render_template('mpo_detail.html', mpo=items[idx])

@app.route('/committees/<int:idx>')
def committee_detail(idx):
    items = load_json(COMMITTEES_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('committees'))
    return render_template('committee_detail.html', committee=items[idx])

@app.route('/students/<int:idx>')
def student_detail(idx):
    items = load_json(STUDENTS_FILE)
    if idx < 0 or idx >= len(items):
        return redirect(url_for('students'))
    return render_template('student_detail.html', student=items[idx])

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
            # if don't upload file like photo or pdf, redirect to same page
            if not request.files.get('file') and not request.files.get('photo') and json_file != NEWS_FILE:
                flash('No file uploaded.', 'error')
                return redirect(request.path)
            # if upload file, but no title or description, set default values   
            title = request.form.get('title', '').strip()
            desc = request.form.get('description', '').strip()
            if not title or not desc:
                title = "Untitled"
                desc = "No description"
            new_item = {'timestamp': datetime.utcnow().isoformat(), 'title': title, 'description': desc}
            if upload_dir and 'photo' in request.files:
                file = request.files['photo']
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_dir, filename))
                new_item['filename'] = filename
            elif json_file != NEWS_FILE:
                flash('No file uploaded.', 'error')
                return redirect(request.path)
            items.insert(0, new_item)
            save_json(json_file, items)
            flash('New item added!', 'success')
            return redirect(request.path)

    return view, action
# Results admin
res_view, res_action = admin_crud(
    RESULTS_FILE,
    UPLOAD_DIRS['results'],
    template_name='result_admin.html'
)
app.add_url_rule('/admin/results', 'result_admin', admin_required(res_view), methods=['GET'])
app.add_url_rule('/admin/results', 'result_admin_post', admin_required(res_action), methods=['POST'])
# Routine admin
rou_view, rou_action = admin_crud(
    ROUTINE_FILE,
    UPLOAD_DIRS['routine'],
    template_name='routine_admin.html'
)
app.add_url_rule('/admin/routine', 'routine_admin', admin_required(rou_view), methods=['GET'])
app.add_url_rule('/admin/routine', 'routine_admin_post', admin_required(rou_action), methods=['POST'])

# Gallery admin
@app.route('/admin/gallery', methods=['GET', 'POST'])
@admin_required
def gallery_admin():
    items = load_json(GALLERY_FILE)
    last = items[0] if items else None

    if request.method == 'POST':
        # 1) Authenticate
        if request.form.get('password') != ADMIN_PASSWORD:
            flash('Invalid password.', 'error')
            return redirect(url_for('gallery_admin'))

        action = request.form.get('action')
        # 2) Delete last
        if action == 'delete' and last:
            for fn in last.get('images', []):
                try:
                    os.remove(os.path.join(UPLOAD_DIRS['gallery'], fn))
                except OSError:
                    pass
            items.pop(0)
            save_json(GALLERY_FILE, items)
            flash('Last gallery item deleted.', 'success')
            return redirect(url_for('gallery_admin'))

        # 3) Add new (multiple photos)
        title = request.form.get('title','').strip()
        desc  = request.form.get('description','').strip()
        files = request.files.getlist('photos')
        if not title or not desc or not files:
            flash('All fields and at least one photo are required.', 'error')
            return redirect(url_for('gallery_admin'))

        saved = []
        for file in files:
            if file and file.filename:
                fn = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_DIRS['gallery'], fn))
                saved.append(fn)

        new_item = {
            'timestamp': datetime.utcnow().isoformat(),
            'title': title,
            'description': desc,
            'images': saved
        }
        items.insert(0, new_item)
        save_json(GALLERY_FILE, items)
        flash('Gallery item posted!', 'success')
        return redirect(url_for('gallery_admin'))

    return render_template('gallery_admin.html', last=last)


# Register CRUD routes
# News
news_view, news_action = admin_crud(NEWS_FILE, template_name='news_admin.html')
app.add_url_rule('/admin/news', 'news_admin', admin_required(news_view), methods=['GET'])
app.add_url_rule('/admin/news', 'news_admin_post', admin_required(news_action), methods=['POST'])

# Teachers
teach_view, teach_action = admin_crud(TEACHERS_FILE, UPLOAD_DIRS['teachers'], 'teacher_admin.html')
app.add_url_rule('/admin/teachers', 'teacher_admin', admin_required(teach_view), methods=['GET'])
app.add_url_rule('/admin/teachers', 'teacher_admin_post', admin_required(teach_action), methods=['POST'])
# MPOs
teach_view, teach_action = admin_crud(MPOS_FILE, UPLOAD_DIRS['mpos'], 'mpo_admin.html')
app.add_url_rule('/admin/mpos', 'mpo_admin', admin_required(teach_view), methods=['GET'])
app.add_url_rule('/admin/mpos', 'mpo_admin_post', admin_required(teach_action), methods=['POST'])
# committees
comm_view, comm_action = admin_crud(COMMITTEES_FILE, UPLOAD_DIRS['committees'], 'committee_admin.html')
app.add_url_rule('/admin/committees', 'committee_admin', admin_required(comm_view), methods=['GET'])
app.add_url_rule('/admin/committees', 'committee_admin_post', admin_required(comm_action), methods=['POST'])
# Students
stud_view, stud_action = admin_crud(STUDENTS_FILE, UPLOAD_DIRS['students'], 'student_admin.html')
app.add_url_rule('/admin/students', 'student_admin', admin_required(stud_view), methods=['GET'])
app.add_url_rule('/admin/students', 'student_admin_post', admin_required(stud_action), methods=['POST'])

if __name__ == '__main__':
    # app.run(debug=True)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)




