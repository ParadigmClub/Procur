from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import io
import os
# Paradigm ❤️ Souvenir Club
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# ok ish

uri = os.environ.get('DATABASE_URL')
if not uri:
    print("No DATABASE_URL found")

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"]) 


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='participant')  # admin, coordinator, participant
    school = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    event_registrations = db.relationship('EventRegistration', backref='user', lazy='dynamic', cascade='all, delete-orphan')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    max_participants = db.Column(db.Integer, default=100)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)  # sports, academic, cultural, etc.
    require_approval = db.Column(db.Boolean, default=False)
    team_allowed = db.Column(db.Boolean, default=False)
    team_min = db.Column(db.Integer, default=1)
    team_max = db.Column(db.Integer, default=1)
    

    creator = db.relationship('User', backref='created_events', foreign_keys=[created_by])
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, confirmed, cancelled
    notes = db.Column(db.Text)
    team_name = db.Column(db.String(120))

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    activity = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    event = db.relationship('Event')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime)
    is_pinned = db.Column(db.Boolean, default=False)

class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255))

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)

class EmailVerificationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)

class EventMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255))

class EventCoordinator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(200))

class EventAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(50))
    object_id = db.Column(db.Integer)
    snapshot = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def ensure_database_initialized():

    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@school.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            school='Main School'
        )
        db.session.add(admin)
        db.session.commit()


with app.app_context():
    try:
        ensure_database_initialized()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")

        try:
            db.create_all()
            print("Tables created successfully")
        except Exception as e2:
            print(f"Table creation error: {str(e2)}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/test-db')
def test_db():
    try:

        db.session.execute('SELECT 1')
        user_count = User.query.count()
        return jsonify({
            'status': 'success',
            'message': 'Database connection working',
            'user_count': user_count,
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '://' in app.config['SQLALCHEMY_DATABASE_URI'] else 'sqlite'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '://' in app.config['SQLALCHEMY_DATABASE_URI'] else 'sqlite'
        }), 500

@app.route('/')
def index():
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.now(),
        Event.status == 'upcoming'
    ).order_by(Event.event_date).limit(6).all()
    
    ongoing_events = Event.query.filter(
        Event.status == 'ongoing'
    ).all()
    

    for event in upcoming_events:
        event.registration_count = EventRegistration.query.filter_by(event_id=event.id).count()
    

    for event in ongoing_events:
        event.registration_count = EventRegistration.query.filter_by(event_id=event.id).count()
    
    events = Event.query.all()  # Fetches a list, not a query object

    now_dt = datetime.utcnow()
    announcements = Announcement.query.filter(
        (Announcement.starts_at <= now_dt),
        ((Announcement.ends_at == None) | (Announcement.ends_at >= now_dt))
    ).order_by(Announcement.is_pinned.desc(), Announcement.starts_at.desc()).all()
    return render_template('index.html', upcoming_events=upcoming_events, ongoing_events=ongoing_events, events=events, announcements=announcements)

@app.context_processor
def inject_nav_notifications():
    if current_user.is_authenticated:
        unread = Notification.query.filter_by(user_id=current_user.id, read_at=None).order_by(Notification.created_at.desc()).limit(5).all()
        count = Notification.query.filter_by(user_id=current_user.id, read_at=None).count()
        return dict(nav_notifications=unread, nav_notifications_count=count)
    return dict(nav_notifications=[], nav_notifications_count=0)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            school = request.form.get('school')
            

            if not all([username, email, password, school]):
                flash('All fields are required', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('register.html')
            

            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                school=school
            )
            

            db.session.add(user)
            db.session.flush()  # Get the user ID without committing
            

            token = uuid.uuid4().hex
            db.session.add(EmailVerificationToken(user_id=user.id, token=token))
            db.session.add(Notification(user_id=user.id, title='Verify your email', body='Please verify your email to unlock full features.'))
            

            db.session.commit()
            
            print(f"User {username} registered successfully with ID {user.id}")
            print(f"Email verification link: http://localhost:5000/verify/{token}")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    registered_events = []
    
    for reg in user_events:
        if reg.status == 'confirmed':
            event = Event.query.get(reg.event_id)
            if event:
                registered_events.append(event)
    
    if current_user.role in ['admin', 'coordinator']:
        created_events = Event.query.filter_by(created_by=current_user.id).all()

        for event in created_events:
            event.registration_count = EventRegistration.query.filter_by(event_id=event.id).count()
    else:
        created_events = []
    
    return render_template('dashboard.html',
                         registered_events=registered_events,
                         created_events=created_events)

@app.route('/events')
def events():
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    search_query = request.args.get('q', '').strip()
    date_range = request.args.get('date_range', '')
    sort_by = request.args.get('sort_by', 'date_asc')
    
    query = Event.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Event.title.ilike(like),
                Event.description.ilike(like),
                Event.location.ilike(like),
                Event.category.ilike(like)
            )
        )
    if date_range:
        now_dt = datetime.now()
        if date_range == 'today':
            start = datetime(now_dt.year, now_dt.month, now_dt.day)
            end = start + timedelta(days=1)
            query = query.filter(Event.event_date >= start, Event.event_date < end)
        elif date_range == 'week':
            end = now_dt + timedelta(days=7)
            query = query.filter(Event.event_date >= now_dt, Event.event_date < end)
        elif date_range == 'month':
            end = now_dt + timedelta(days=30)
            query = query.filter(Event.event_date >= now_dt, Event.event_date < end)
        elif date_range == 'next_month':
            end = now_dt + timedelta(days=60)
            start = now_dt + timedelta(days=30)
            query = query.filter(Event.event_date >= start, Event.event_date < end)
    
    if sort_by == 'date_desc':
        query = query.order_by(Event.event_date.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Event.title.asc())
    elif sort_by == 'popular':

        subq = db.session.query(EventRegistration.event_id, db.func.count(EventRegistration.id).label('reg_count')).group_by(EventRegistration.event_id).subquery()
        query = query.outerjoin(subq, Event.id == subq.c.event_id).order_by(db.desc(subq.c.reg_count.nullslast()))
    else:
        query = query.order_by(Event.event_date.asc())

    events = query.all()
    

    for event in events:
        event.registration_count = EventRegistration.query.filter_by(event_id=event.id).count()
    
    categories = [c[0] for c in db.session.query(Event.category).distinct().all()]
    print(type(events))  # Should print <class 'list'>
    print(type(categories))  # Should print <class 'list'>
    
    return render_template('events.html', events=events, categories=categories, category=category, status=status)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    schedule = Schedule.query.filter_by(event_id=event_id).order_by(Schedule.start_time).all()
    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.created_at.desc()).all()
    
    is_registered = False
    if current_user.is_authenticated:
        registration = EventRegistration.query.filter_by(
            event_id=event_id, 
            user_id=current_user.id
        ).first()
        is_registered = registration is not None
    
    return render_template('event_detail.html', 
                         event=event, 
                         registrations=registrations,
                         schedule=schedule,
                         comments=comments,
                         is_registered=is_registered,
                         now=datetime.now())

@app.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    

    existing_registration = EventRegistration.query.filter_by(
        event_id=event_id, 
        user_id=current_user.id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this event', 'info')
        return redirect(url_for('event_detail', event_id=event_id))
    

    if datetime.now() > event.registration_deadline:
        flash('Registration deadline has passed', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    

    current_registrations = EventRegistration.query.filter_by(event_id=event_id).count()
    if current_registrations >= event.max_participants:

        existing_wait = Waitlist.query.filter_by(event_id=event_id, user_id=current_user.id).first()
        if not existing_wait:
            position = (db.session.query(db.func.max(Waitlist.position)).filter_by(event_id=event_id).scalar() or 0) + 1
            db.session.add(Waitlist(event_id=event_id, user_id=current_user.id, position=position))
            db.session.commit()
            flash('Event is full. You have been added to the waitlist.', 'info')
        else:
            flash('Event is full and you are already on the waitlist.', 'info')
        return redirect(url_for('event_detail', event_id=event_id))
    

    qr_token = str(uuid.uuid4())

    notes_value = f"qr:{qr_token}"
    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.id,
        notes=notes_value
    )
    db.session.add(registration)
    db.session.commit()


    if event.require_approval:
        registration.status = 'registered'
    else:
        registration.status = 'confirmed'

    recipients = [event.created_by]
    for ec in EventCoordinator.query.filter_by(event_id=event.id).all():
        recipients.append(ec.user_id)
    for rid in set(recipients):
        db.session.add(Notification(user_id=rid, title='New Event Registration', body=f'{current_user.username} registered for {event.title}'))
    db.session.add(AuditLog(actor_id=current_user.id, action='register_event', object_type='event', object_id=event.id, snapshot=f'user={current_user.id}'))
    db.session.commit()
    
    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/event/<int:event_id>/toggle_approval')
@login_required
def toggle_event_approval(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.role != 'admin' and current_user.id != event.created_by:
        flash('Access denied', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    event.require_approval = not event.require_approval
    db.session.commit()
    flash(f'Registration approval requirement set to {event.require_approval}', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/event/<int:event_id>/upload', methods=['POST'])
@login_required
def upload_event_file(event_id):
    event = Event.query.get_or_404(event_id)
    if not user_can_manage_event(current_user, event):
        flash('Access denied', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    f = request.files.get('file')
    if not f or not f.filename:
        flash('No file selected', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    os.makedirs('uploads', exist_ok=True)
    safe_name = f"{event_id}_{int(datetime.utcnow().timestamp())}_{f.filename}"
    path = os.path.join('uploads', safe_name)
    f.save(path)
    db.session.add(EventAttachment(event_id=event_id, filename=safe_name))
    db.session.commit()
    flash('File uploaded', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    event = Event.query.get_or_404(event_id)
    body = request.form.get('body', '').strip()
    if not body:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    comment = Comment(event_id=event.id, user_id=current_user.id, body=body)
    db.session.add(comment)

    event_creator_id = event.created_by
    if event_creator_id != current_user.id:
        db.session.add(Notification(user_id=event_creator_id, title='New Comment', body=f'{current_user.username} commented on {event.title}'))
    for ec in EventCoordinator.query.filter_by(event_id=event.id).all():
        if ec.user_id != current_user.id and ec.user_id != event_creator_id:
            db.session.add(Notification(user_id=ec.user_id, title='New Comment', body=f'{current_user.username} commented on {event.title}'))
    db.session.add(AuditLog(actor_id=current_user.id, action='add_comment', object_type='event', object_id=event.id))
    db.session.commit()
    flash('Comment posted', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/event/<int:event_id>/calendar.ics')
def event_ics(event_id):
    event = Event.query.get_or_404(event_id)
    ics = []
    ics.append('BEGIN:VCALENDAR')
    ics.append('VERSION:2.0')
    ics.append('PRODID:-//Procur//EN')
    ics.append('BEGIN:VEVENT')
    ics.append(f'SUMMARY:{event.title}')
    ics.append(f'DTSTART:{event.event_date.strftime("%Y%m%dT%H%M%S")}')

    end_dt = event.event_date + timedelta(hours=2)
    ics.append(f'DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}')
    ics.append(f'LOCATION:{event.location}')
    ics.append(f'DESCRIPTION:{event.description.replace("\n", " ")}')
    ics.append('END:VEVENT')
    ics.append('END:VCALENDAR')
    ics_content = "\r\n".join(ics)
    return Response(ics_content, mimetype='text/calendar', headers={'Content-Disposition': f'attachment; filename=event_{event.id}.ics'})

@app.route('/calendar/feed.ics')
@login_required
def user_calendar_feed():
    regs = EventRegistration.query.filter_by(user_id=current_user.id).all()
    ics_lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Procur//EN']
    for reg in regs:
        event = Event.query.get(reg.event_id)
        if not event:
            continue
        ics_lines.append('BEGIN:VEVENT')
        ics_lines.append(f'SUMMARY:{event.title}')
        ics_lines.append(f'DTSTART:{event.event_date.strftime("%Y%m%dT%H%M%S")}')
        end_dt = event.event_date + timedelta(hours=2)
        ics_lines.append(f'DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}')
        ics_lines.append(f'LOCATION:{event.location}')
        ics_lines.append(f'DESCRIPTION:{event.description.replace("\n", " ")}')
        ics_lines.append('END:VEVENT')
    ics_lines.append('END:VCALENDAR')
    return Response("\r\n".join(ics_lines), mimetype='text/calendar', headers={'Content-Disposition': 'attachment; filename=my_calendar.ics'})

@app.route('/ticket/<string:qr_token>.png')
@login_required
def ticket_qr(qr_token):

    reg = EventRegistration.query.filter(EventRegistration.user_id == current_user.id, EventRegistration.notes.like(f'%qr:{qr_token}%')).first()
    if not reg:
        flash('Invalid ticket token', 'error')
        return redirect(url_for('dashboard'))
    try:
        import qrcode
        img = qrcode.make(f'CHECKIN:{qr_token}')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception:
        flash('QR generation failed', 'error')
        return redirect(url_for('dashboard'))

@app.route('/checkin/<string:qr_token>')
@login_required
def checkin(qr_token):

    if current_user.role not in ['admin', 'coordinator']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    reg = EventRegistration.query.filter(EventRegistration.notes.like(f'%qr:{qr_token}%')).first()
    if not reg:
        flash('Invalid token', 'error')
        return redirect(url_for('dashboard'))
    existing = CheckIn.query.filter_by(event_id=reg.event_id, user_id=reg.user_id).first()
    if existing:
        flash('Already checked in', 'info')
        return redirect(url_for('event_detail', event_id=reg.event_id))
    db.session.add(CheckIn(event_id=reg.event_id, user_id=reg.user_id))
    db.session.commit()
    flash('Check-in successful', 'success')
    return redirect(url_for('event_detail', event_id=reg.event_id))

@app.route('/admin/export/<string:what>.csv')
@login_required
def export_csv(what):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    if what == 'users':
        writer.writerow(['id', 'username', 'email', 'school', 'role', 'created_at'])
        for u in User.query.all():
            writer.writerow([u.id, u.username, u.email, u.school, u.role, u.created_at])
    elif what == 'events':
        writer.writerow(['id', 'title', 'category', 'date', 'location', 'status', 'max_participants'])
        for e in Event.query.all():
            writer.writerow([e.id, e.title, e.category, e.event_date, e.location, e.status, e.max_participants])
    elif what == 'registrations':
        writer.writerow(['id', 'event_id', 'event_title', 'user_id', 'username', 'status', 'registration_date'])
        regs = EventRegistration.query.all()
        for r in regs:
            ev = Event.query.get(r.event_id)
            us = User.query.get(r.user_id)
            writer.writerow([r.id, r.event_id, ev.title if ev else '', r.user_id, us.username if us else '', r.status, r.registration_date])
    else:
        flash('Unknown export type', 'error')
        return redirect(url_for('admin_panel'))
    csv_content = output.getvalue()
    return Response(csv_content, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={what}.csv'})


@app.route('/verify/request')
@login_required
def request_verification():
    existing = EmailVerificationToken.query.filter_by(user_id=current_user.id, verified_at=None).first()
    if existing:
        token = existing.token
    else:
        token = uuid.uuid4().hex
        db.session.add(EmailVerificationToken(user_id=current_user.id, token=token))
        db.session.commit()
    flash('Verification link generated. Check console if email is not configured.', 'info')
    print(f"Email verification link: http://localhost:5000/verify/{token}")
    return redirect(url_for('dashboard'))

@app.route('/verify/<string:token>')
def verify_email(token):
    rec = EmailVerificationToken.query.filter_by(token=token).first()
    if not rec or rec.verified_at:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('login'))
    rec.verified_at = datetime.utcnow()

    db.session.add(UserMeta(user_id=rec.user_id, key='email_verified', value='1'))
    db.session.add(Notification(user_id=rec.user_id, title='Email verified', body='Thanks for verifying your email.'))
    db.session.add(AuditLog(actor_id=rec.user_id, action='verify_email', object_type='user', object_id=rec.user_id))
    db.session.commit()
    flash('Email verified successfully', 'success')
    return redirect(url_for('dashboard'))


@app.route('/password/forgot', methods=['GET', 'POST'])
def password_forgot():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user:
            token = uuid.uuid4().hex
            db.session.add(PasswordResetToken(user_id=user.id, token=token))
            db.session.commit()
            print(f"Password reset link: http://localhost:5000/password/reset/{token}")
        flash('If the account exists, a reset link has been generated (see console).', 'info')
        return redirect(url_for('login'))
    return render_template('password_forgot.html')

@app.route('/password/reset/<string:token>', methods=['GET', 'POST'])
def password_reset(token):
    rec = PasswordResetToken.query.filter_by(token=token).first()
    if not rec or rec.used_at:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        pw = request.form.get('password')
        if not pw or len(pw) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('password_reset.html')
        user = User.query.get(rec.user_id)
        user.password_hash = generate_password_hash(pw)
        rec.used_at = datetime.utcnow()
        db.session.add(AuditLog(actor_id=user.id, action='password_reset', object_type='user', object_id=user.id))
        db.session.commit()
        flash('Password has been reset. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('password_reset.html')


def user_can_manage_event(user: User, event: Event) -> bool:
    if user.role == 'admin':
        return True
    if user.role == 'coordinator' and event.created_by == user.id:
        return True
    return EventCoordinator.query.filter_by(event_id=event.id, user_id=user.id).first() is not None

@app.route('/event/<int:event_id>/registration/<int:reg_id>/approve')
@login_required
def approve_registration(event_id, reg_id):
    event = Event.query.get_or_404(event_id)
    if not user_can_manage_event(current_user, event):
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    reg = EventRegistration.query.get_or_404(reg_id)
    reg.status = 'confirmed'
    db.session.add(Notification(user_id=reg.user_id, title='Registration Approved', body=f'Your registration for {event.title} was approved.'))
    db.session.add(AuditLog(actor_id=current_user.id, action='approve_registration', object_type='registration', object_id=reg.id))
    db.session.commit()
    flash('Registration approved', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/notifications')
@login_required
def notifications_list():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=items)

@app.route('/notifications/<int:notif_id>/read')
@login_required
def notifications_mark_read(notif_id):
    n = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    n.read_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('notifications_list'))

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role not in ['admin', 'coordinator']:
        flash('You do not have permission to create events', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M'),
            location=request.form.get('location'),
            max_participants=int(request.form.get('max_participants')),
            registration_deadline=datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%dT%H:%M'),
            category=request.form.get('category'),
            created_by=current_user.id,
            require_approval=bool(request.form.get('require_approval')),
            team_allowed=bool(request.form.get('team_allowed')),
            team_min=int(request.form.get('team_min') or 1),
            team_max=int(request.form.get('team_max') or 1)
        )
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    
    return render_template('create_event.html')

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    events = Event.query.all()
    registrations = EventRegistration.query.all()
    

    for event in events:
        event.registration_count = EventRegistration.query.filter_by(event_id=event.id).count()
    
    return render_template('admin.html', users=users, events=events, registrations=registrations)

@app.route('/admin/user/<int:user_id>/toggle_role')
@login_required
def toggle_user_role(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        user.role = 'participant'
    elif user.role == 'participant':
        user.role = 'coordinator'
    else:
        user.role = 'admin'
    
    db.session.commit()
    flash(f'User {user.username} role changed to {user.role}', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/event/<int:event_id>/toggle_status')
@login_required
def toggle_event_status(event_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    event = Event.query.get_or_404(event_id)
    if event.status == 'upcoming':
        event.status = 'ongoing'
    elif event.status == 'ongoing':
        event.status = 'completed'
    else:
        event.status = 'upcoming'
    
    db.session.commit()
    flash(f'Event {event.title} status changed to {event.status}', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        

        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                school='Main School'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
    
    app.run(debug=True)
