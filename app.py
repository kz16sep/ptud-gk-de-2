from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from PIL import Image

# Xóa database cũ nếu tồn tại
if os.path.exists('tasks.db'):
    os.remove('tasks.db')

# Khởi tạo app và database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    avatar_path = db.Column(db.String(200))
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float, nullable=False, default=1.0)
    priority = db.Column(db.String(20), default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def priority_color(self):
        return {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger'
        }.get(self.priority, 'secondary')

    @property
    def current_status(self):
        """Trả về trạng thái hiện tại của task"""
        if self.status == 'completed':
            return 'completed'
        elif self.due_date < datetime.now() and self.status != 'completed':
            return 'overdue'
        elif self.status == 'in_progress':
            return 'in_progress'
        else:
            return 'pending'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    # Lấy tất cả tasks của user hiện tại
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # Tính toán chi tiết về tasks trễ hạn
    now = datetime.now()
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status != 'completed',
        Task.due_date < now
    ).all()
    
    # Phân loại tasks trễ hạn theo mức độ
    critical_overdue = [] # Trễ > 24h
    today_overdue = []   # Trễ < 24h
    
    for task in overdue_tasks:
        hours_overdue = (now - task.due_date).total_seconds() / 3600
        if hours_overdue > 24:
            critical_overdue.append(task)
        else:
            today_overdue.append(task)
    
    overdue_stats = {
        'total': len(overdue_tasks),
        'critical': len(critical_overdue),
        'today': len(today_overdue)
    }
    
    return render_template('index.html', 
                         tasks=tasks, 
                         overdue_stats=overdue_stats,
                         critical_overdue=critical_overdue,
                         today_overdue=today_overdue,
                         now=now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Resize image if needed
        with Image.open(filepath) as img:
            img.thumbnail((200, 200))
            img.save(filepath)
        
        current_user.avatar_path = f'avatars/{filename}'
        db.session.commit()
        flash('Avatar updated successfully')
    
    return redirect(url_for('index'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%dT%H:%M')
        
        # Lấy giờ và phút từ form
        hours = int(request.form.get('hours', 0))
        minutes = int(request.form.get('minutes', 0))
        estimated_hours = hours + (minutes / 60)  # Chuyển đổi thành giờ
            
        priority = request.form.get('priority', 'medium')
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            created_at=datetime.now(),  # Sử dụng thời gian hiện tại
            estimated_hours=estimated_hours,
            priority=priority,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully')
    except Exception as e:
        flash(f'Error adding task: {str(e)}')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return redirect(url_for('index'))
    
    task.status = request.form.get('status')
    if task.status == 'completed':
        task.finished_at = datetime.utcnow()
    
    db.session.commit()
    flash('Task status updated')
    return redirect(url_for('index'))

@app.route('/create-test-tasks')
@login_required
def create_test_tasks():
    try:
        # Overdue task
        overdue_task = Task(
            title="Overdue Task",
            description="This task is 2 days overdue",
            due_date=datetime.utcnow() - timedelta(days=2),
            user_id=current_user.id,
            status='pending',
            estimated_hours=4.0,
            priority='high'
        )
        
        # Due today task
        due_today_task = Task(
            title="Due Today Task",
            description="This task is due today",
            due_date=datetime.utcnow(),
            user_id=current_user.id,
            status='in_progress',
            estimated_hours=2.5,
            priority='medium'
        )
        
        # Future task
        future_task = Task(
            title="Future Task",
            description="This task is due in 3 days",
            due_date=datetime.utcnow() + timedelta(days=3),
            user_id=current_user.id,
            status='pending',
            estimated_hours=1.5,
            priority='low'
        )
        
        # Completed overdue task
        completed_overdue_task = Task(
            title="Completed Overdue Task",
            description="This task was completed but was overdue",
            due_date=datetime.utcnow() - timedelta(days=1),
            user_id=current_user.id,
            status='completed',
            finished_at=datetime.utcnow(),
            estimated_hours=3.0,
            priority='medium'
        )

        db.session.add(overdue_task)
        db.session.add(due_today_task)
        db.session.add(future_task)
        db.session.add(completed_overdue_task)
        db.session.commit()
        
        flash('Test tasks created successfully!')
    except Exception as e:
        flash(f'Error creating test tasks: {str(e)}')
        db.session.rollback()
    
    return redirect(url_for('index'))

# Tạo tất cả bảng trong database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 