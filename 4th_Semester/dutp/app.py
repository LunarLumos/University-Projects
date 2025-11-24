from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime, timedelta
from models import db, Student, Admin, Bus, Route, Booking, Notice
from sqlalchemy import text
from config import Config
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies, unset_jwt_cookies, get_jwt
import bcrypt
from datetime import datetime, timedelta
import warnings
import logging

# Suppress specific warnings but allow normal Flask output
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*relationship.*will copy column.*')
warnings.filterwarnings('ignore', message='.*overlaps.*')

# Allow normal Flask startup messages but suppress debug logs
logging.getLogger('werkzeug').setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Invalid token"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"msg": "Missing token"}), 401
db.init_app(app)

# Create tables (run once)
def create_tables():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        # Ensure 'approved_date' column exists on students table (added in model recently).
        # Try to add it; ignore failures (column already exists or permissions issues).
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN approved_date DATE"))
        except Exception:
            # ignore errors (e.g., column already exists)
            pass
        # Ensure 'start_time' column exists on buses table (may be missing if models were updated)
        try:
            with db.engine.begin() as conn:
                # TIME type for MySQL
                conn.execute(text("ALTER TABLE buses ADD COLUMN start_time TIME"))
        except Exception:
            # ignore errors (e.g., column already exists or permission issues)
            pass
        # Ensure new student registration columns exist (department, student_number, payment_receipt_id, preferred_route_id)
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN department VARCHAR(100)"))
        except Exception:
            pass
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN student_number VARCHAR(50)"))
        except Exception:
            pass
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN payment_receipt_id VARCHAR(100)"))
        except Exception:
            pass
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE students ADD COLUMN preferred_route_id INT"))
        except Exception:
            pass
        
        # Add sample data if not exists
        if not Admin.query.first():
            # Create default admin account
            admin = Admin(
                name='System Admin',
                email='admin@daffodilvarsity.edu.bd',
                password=hash_password('admin123')
            )
            db.session.add(admin)
        
        if not Student.query.filter_by(email='john@daffodilvarsity.edu.bd').first():
            # Create default student account
            student = Student(
                name='John Doe',
                email='john@daffodilvarsity.edu.bd',
                password=hash_password('student123'),
                is_approved=True,
                status='active'
            )
            db.session.add(student)
        else:
            # Update existing student to ensure approved and active
            student = Student.query.filter_by(email='john@daffodilvarsity.edu.bd').first()
            student.is_approved = True
            student.status = 'active'
            student.password = hash_password('student123')  # Reset password just in case
        
        if not Route.query.first():
            # Create sample routes
            routes_data = [
                {
                    'name': 'Campus ⇄ Mirpur',
                    'start': 'DIU Main Campus',
                    'end': 'Mirpur 10',
                    'distance': 15.5,
                    'duration': 45
                },
                {
                    'name': 'Campus ⇄ Uttara',
                    'start': 'DIU Main Campus',
                    'end': 'Uttara Sector 4',
                    'distance': 22.0,
                    'duration': 60
                },
                {
                    'name': 'Campus ⇄ Dhanmondi',
                    'start': 'DIU Main Campus',
                    'end': 'Dhanmondi 27',
                    'distance': 18.0,
                    'duration': 50
                },
                {
                    'name': 'Campus ⇄ Gulshan',
                    'start': 'DIU Main Campus',
                    'end': 'Gulshan Circle 1',
                    'distance': 25.0,
                    'duration': 70
                },
                {
                    'name': 'Campus ⇄ Banani',
                    'start': 'DIU Main Campus',
                    'end': 'Banani DOHS',
                    'distance': 20.0,
                    'duration': 55
                }
            ]
            
            routes = []
            for route_data in routes_data:
                route = Route(
                    route_name=route_data['name'],
                    start_point=route_data['start'],
                    end_point=route_data['end'],
                    distance=route_data['distance'],
                    duration=route_data['duration'],
                    status='active'
                )
                routes.append(route)
                db.session.add(route)
            db.session.commit()  # Commit routes first to get IDs
        
        if not Bus.query.first():
            # Create sample buses with start times for each route
            from datetime import time
            
            buses_data = [
                # Route 1: Campus ⇄ Mirpur
                {'number': '🌼 DIU BUS 01', 'capacity': 40, 'driver': 'Abdul Karim', 'route_id': 1, 'time': time(8, 0)},
                {'number': '🌼 DIU BUS 02', 'capacity': 35, 'driver': 'Rahim Mia', 'route_id': 1, 'time': time(9, 30)},
                {'number': '🌼 DIU BUS 03', 'capacity': 40, 'driver': 'Karim Hossain', 'route_id': 1, 'time': time(11, 0)},
                {'number': '🌼 DIU BUS 04', 'capacity': 35, 'driver': 'Jahangir Alam', 'route_id': 1, 'time': time(14, 30)},
                {'number': '🌼 DIU BUS 05', 'capacity': 40, 'driver': 'Mohammad Ali', 'route_id': 1, 'time': time(16, 0)},
                
                # Route 2: Campus ⇄ Uttara
                {'number': '🌼 DIU BUS 06', 'capacity': 40, 'driver': 'Hasan Mahmud', 'route_id': 2, 'time': time(8, 15)},
                {'number': '🌼 DIU BUS 07', 'capacity': 35, 'driver': 'Rafiq Islam', 'route_id': 2, 'time': time(10, 0)},
                {'number': '🌼 DIU BUS 08', 'capacity': 40, 'driver': 'Sultan Ahmed', 'route_id': 2, 'time': time(12, 30)},
                {'number': '🌼 DIU BUS 09', 'capacity': 35, 'driver': 'Belal Hossain', 'route_id': 2, 'time': time(15, 0)},
                {'number': '🌼 DIU BUS 10', 'capacity': 40, 'driver': 'Nazmul Haque', 'route_id': 2, 'time': time(17, 30)},
                
                # Route 3: Campus ⇄ Dhanmondi
                {'number': '🌼 DIU BUS 11', 'capacity': 35, 'driver': 'Shamim Reza', 'route_id': 3, 'time': time(8, 45)},
                {'number': '🌼 DIU BUS 12', 'capacity': 40, 'driver': 'Fazlul Karim', 'route_id': 3, 'time': time(10, 30)},
                {'number': '🌼 DIU BUS 13', 'capacity': 35, 'driver': 'Anwar Hossain', 'route_id': 3, 'time': time(13, 15)},
                {'number': '🌼 DIU BUS 14', 'capacity': 40, 'driver': 'Babul Mia', 'route_id': 3, 'time': time(15, 45)},
                
                # Route 4: Campus ⇄ Gulshan
                {'number': '🌼 DIU BUS 15', 'capacity': 40, 'driver': 'Rashed Khan', 'route_id': 4, 'time': time(9, 0)},
                {'number': '🌼 DIU BUS 16', 'capacity': 35, 'driver': 'Kamal Uddin', 'route_id': 4, 'time': time(11, 30)},
                {'number': '🌼 DIU BUS 17', 'capacity': 40, 'driver': 'Jamal Ahmed', 'route_id': 4, 'time': time(14, 0)},
                {'number': '🌼 DIU BUS 18', 'capacity': 35, 'driver': 'Salim Reza', 'route_id': 4, 'time': time(16, 30)},
                
                # Route 5: Campus ⇄ Banani
                {'number': '🌼 DIU BUS 19', 'capacity': 35, 'driver': 'Tariq Rahman', 'route_id': 5, 'time': time(9, 15)},
                {'number': '🌼 DIU BUS 20', 'capacity': 40, 'driver': 'Nasir Uddin', 'route_id': 5, 'time': time(11, 45)},
                {'number': '🌼 DIU BUS 21', 'capacity': 35, 'driver': 'Faruk Ahmed', 'route_id': 5, 'time': time(14, 15)},
                {'number': '🌼 DIU BUS 22', 'capacity': 40, 'driver': 'Monir Hossain', 'route_id': 5, 'time': time(16, 45)}
            ]
            
            for bus_data in buses_data:
                bus = Bus(
                    bus_number=bus_data['number'],
                    capacity=bus_data['capacity'],
                    driver_name=bus_data['driver'],
                    route_id=bus_data['route_id'],
                    start_time=bus_data['time'],
                    status='active'
                )
                db.session.add(bus)
        
        if not Notice.query.first():
            # Create sample notice
            notice = Notice(
                title='Welcome!',
                content='New semester registration is open!',
                posted_date=datetime.utcnow(),
                status='active'
            )
            db.session.add(notice)
        
        db.session.commit()

# --- UTILS ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def current_date():
    return datetime.utcnow().date()

def current_time():
    return datetime.utcnow().time()

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        role = request.form['role']
        identifier = request.form['identifier']
        password = request.form['password']

        print(f"Login attempt: role={role}, identifier={identifier}")

        if role == 'student':
            student = Student.query.filter_by(email=identifier).first()
            print(f"Student found: {student}")
            if student:
                print(f"Student is_approved: {student.is_approved}")
                print(f"Password check: {verify_password(password, student.password)}")
            if student and verify_password(password, student.password):
                if not student.is_approved:
                    print("Student not approved by admin.")
                    flash('Not approved by admin', 'error')
                    return redirect(url_for('login'))
                if student.semester_expiry and current_date() >= student.semester_expiry:
                    print("Student semester approval expired.")
                    flash('Your semester approval has expired. Please contact admin for renewal.', 'error')
                    return redirect(url_for('login'))
                print("Student login successful.")
                token = create_access_token(identity=str(student.student_id), additional_claims={'role': 'student', 'name': student.name})
                response = make_response(redirect(url_for('dashboard')))
                set_access_cookies(response, token)
                return response
            else:
                print("Invalid student credentials.")
                flash('Invalid student credentials', 'error')
                return redirect(url_for('login'))
        else:
            admin = Admin.query.filter_by(email=identifier).first()
            print(f"Admin found: {admin}")
            if admin:
                print(f"Password check: {verify_password(password, admin.password)}")
            if admin and verify_password(password, admin.password):
                print("Admin login successful.")
                token = create_access_token(identity=str(admin.admin_id), additional_claims={'role': 'admin', 'name': admin.name})
                response = make_response(redirect(url_for('admin_dashboard')))
                set_access_cookies(response, token)
                return response
            else:
                print("Invalid admin credentials.")
                flash('Invalid admin credentials', 'error')
                return redirect(url_for('login'))
    # Provide available routes to the login page so registration form can reference them
    routes = Route.query.filter_by(status='active').all()
    # If redirected here after registration, show the registration success message only on the login page
    if request.method == 'GET' and request.args.get('registered'):
        flash('Registration submitted! Wait for admin approval.', 'success')
    return render_template('login.html', routes=routes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Render registration page on GET
    if request.method == 'GET':
        routes = Route.query.filter_by(status='active').all()
        return render_template('register.html', routes=routes)
    # Collect registration fields
    name = request.form.get('name')
    email = request.form.get('email')
    raw_password = request.form.get('password')
    department = request.form.get('department')
    student_number = request.form.get('student_number')
    preferred_route = request.form.get('preferred_route')
    payment_receipt_id = request.form.get('payment_receipt_id')

    if not name or not email or not raw_password:
        flash('Name, email and password are required for registration', 'error')
        return redirect(url_for('register'))

    # Only allow DIU email addresses
    try:
        email_l = email.strip().lower()
    except Exception:
        flash('Invalid email address', 'error')
        return redirect(url_for('register'))

    if not email_l.endswith('@diu.edu.bd'):
        flash('Registration is restricted to DIU email addresses (must end with @diu.edu.bd)', 'error')
        return redirect(url_for('register'))

    if Student.query.filter_by(email=email_l).first():
        flash('Email already registered', 'error')
        return redirect(url_for('register'))

    if student_number and Student.query.filter_by(student_number=student_number).first():
        flash('Student number already registered', 'error')
        return redirect(url_for('login'))

    if payment_receipt_id and Student.query.filter_by(payment_receipt_id=payment_receipt_id).first():
        flash('Payment receipt ID already used', 'error')
        return redirect(url_for('register'))

    password = hash_password(raw_password)

    new_student = Student(
        name=name,
        email=email_l,
        password=password,
        department=department,
        student_number=student_number,
        payment_receipt_id=payment_receipt_id,
        preferred_route_id=int(preferred_route) if preferred_route else None,
        is_approved=False,
        status='pending'
    )
    db.session.add(new_student)
    db.session.commit()
    # Redirect to login and show the registration success message there (prevents flash from leaking to other pages)
    return redirect(url_for('login', registered='1'))

@app.route('/logout')
@jwt_required(optional=True)
def logout():
    response = make_response(redirect(url_for('login')))
    unset_jwt_cookies(response)
    return response

# --- STUDENT DASHBOARD ---
@app.route('/dashboard')
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return redirect(url_for('login'))
    
    student = Student.query.get(user_id)
    if not student.is_approved:
        flash('Not approved by admin', 'error')
        return redirect(url_for('login'))
    if student.semester_expiry and current_date() >= student.semester_expiry:
        flash('Your semester approval has expired. Please contact admin for renewal.', 'error')
        return redirect(url_for('login'))
    
    notices = Notice.query.filter_by(status='active').all()
    
    # Get all routes
    all_routes = Route.query.filter_by(status='active').all()
    
    # Get all buses
    buses = Bus.query.filter_by(status='active').all()
    
    # Current time for filtering bookable routes
    from datetime import datetime, timedelta
    now = datetime.now()
    today = current_date()

    # Determine active (running/upcoming) bookings for this student for today
    active_bookings_today_list = []
    try:
        todays_bookings = Booking.query.filter_by(student_id=student.student_id, booking_date=today).all()
        # upcoming bookings: departure datetime > now
        active_bookings_today_list = sorted(
            [b for b in todays_bookings if datetime.combine(today, b.departure_time) > now],
            key=lambda b: b.departure_time
        )
        active_bookings_today = len(active_bookings_today_list)
    except Exception:
        active_bookings_today_list = []
        active_bookings_today = 0
    
    # Filter routes to only show those with bookable departure times (today, at least 1 hour from now)
    bookable_routes = []
    for route in all_routes:
        route_times = route.get_departure_times()
        has_bookable_time = False
        
        for route_time in route_times:
            departure_datetime = datetime.combine(today, route_time)
            if now < departure_datetime - timedelta(hours=1):
                has_bookable_time = True
                break
        
        if has_bookable_time:
            bookable_routes.append(route)

    # Compute next bus per route on server side to avoid client timezone issues
    from datetime import datetime
    now = datetime.now()
    next_bus_by_route = {}
    for route in bookable_routes:
        route_buses = [bus for bus in buses if bus.route_id == route.route_id and bus.start_time]
        next_bus = None
        min_diff = None
        for bus in route_buses:
            for t in [bus.start_time]:
                departure_dt = datetime.combine(current_date(), t)
                diff = (departure_dt - now).total_seconds()
                if diff > 0 and (min_diff is None or diff < min_diff):
                    min_diff = diff
                    # format a human-friendly display time as well
                    display_time = datetime(2000, 1, 1, t.hour, t.minute).strftime('%I:%M %p')
                    next_bus = {
                        'bus_number': bus.bus_number,
                        'departure_time': t.strftime('%H:%M'),
                        'display_time': display_time,
                        'seconds_until': int(diff)
                    }
        if next_bus:
            next_bus_by_route[route.route_id] = next_bus
    # Build a normalized list of times per route (strings 'HH:MM') combining bus.start_time and route departure times.
    route_times_map = {}
    from datetime import datetime as _dt
    for route in bookable_routes:
        times_set = set()
        # add times from buses (if populated)
        for bus in buses:
            try:
                if bus.route_id == route.route_id and getattr(bus, 'start_time', None):
                    times_set.add(bus.start_time.strftime('%H:%M'))
            except Exception:
                # ignore any odd types
                pass
        # add times from route departure_times as fallback
        for t in route.get_departure_times():
            try:
                times_set.add(t.strftime('%H:%M'))
            except Exception:
                pass

        # sort times chronologically
        def _time_key(s):
            return _dt.strptime(s, '%H:%M')

        route_times_map[route.route_id] = sorted(list(times_set), key=_time_key)
    
    return render_template('dashboard.html', student=student, notices=notices, now=datetime.utcnow().date(), routes=bookable_routes, buses=buses, role=claims['role'], next_bus_by_route=next_bus_by_route, route_times_map=route_times_map, active_bookings_today=active_bookings_today, active_bookings_today_list=active_bookings_today_list)

@app.route('/status')
@jwt_required()
def status():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return redirect(url_for('login'))
    student = Student.query.get(user_id)
    if not student.is_approved:
        flash('Not approved by admin', 'error')
        return redirect(url_for('login'))
    if student.semester_expiry and current_date() >= student.semester_expiry:
        flash('Your semester approval has expired. Please contact admin for renewal.', 'error')
        return redirect(url_for('login'))
    semester_valid = student.semester_expiry and current_date() < student.semester_expiry
    
    # Calculate booking statistics
    from datetime import datetime, timedelta
    now = datetime.utcnow().date()
    current_month_start = now.replace(day=1)
    week_ago = now - timedelta(days=7)
    
    # Get booking counts
    total_bookings = len(student.bookings)
    this_month_bookings = len([b for b in student.bookings if b.booking_date >= current_month_start])
    this_week_bookings = len([b for b in student.bookings if b.booking_date >= week_ago])
    
    return render_template('status.html', 
                         student=student, 
                         semester_valid=semester_valid, 
                         now=now, 
                         role=claims['role'],
                         total_bookings=total_bookings,
                         this_month_bookings=this_month_bookings,
                         this_week_bookings=this_week_bookings)

@app.route('/routes')
@jwt_required()
def routes_page():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] == 'student':
        student = Student.query.get(user_id)
        if not student.is_approved:
            flash('Not approved by admin', 'error')
            return redirect(url_for('login'))
        if student.semester_expiry and current_date() >= student.semester_expiry:
            flash('Your semester approval has expired. Please contact admin for renewal.', 'error')
            return redirect(url_for('login'))
    
    routes = Route.query.filter_by(status='active').all()
    # Special routes that require explicit registration: Campus ⇄ Banani and Campus ⇄ Gulshan
    special_route_names = ['Campus ⇄ Banani', 'Campus ⇄ Gulshan']
    special_routes = [r for r in routes if r.route_name in special_route_names]
    special_route_ids = [r.route_id for r in special_routes]

    # If current user is a student and not registered for a special route, hide those special routes
    if claims['role'] == 'student':
        try:
            pref = getattr(student, 'preferred_route_id', None)
            # If student did not register specifically for a special route, filter them out
            if not pref or pref not in special_route_ids:
                routes = [r for r in routes if r.route_id not in special_route_ids]
        except Exception:
            # conservative fallback: hide special routes
            routes = [r for r in routes if r.route_id not in special_route_ids]
    buses = Bus.query.filter_by(status='active').order_by(Bus.route_id).all()
    today = current_date()
    bookings = Booking.query.filter_by(booking_date=today).all()
    
    # Current time for booking restrictions
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # Group buses by route and calculate availability for each route time
    routes_with_buses = []
    for route in routes:
        route_buses = [bus for bus in buses if bus.route_id == route.route_id]
        all_route_times = route.get_departure_times()
        
        # Separate times by direction based on time of day
        # Times before 12:00 PM are "to campus", times at/after 12:00 PM are "from campus"
        noon = datetime.strptime('12:00', '%H:%M').time()
        to_campus_times = [t for t in all_route_times if t < noon]
        from_campus_times = [t for t in all_route_times if t >= noon]
        
        # Calculate availability for to_campus times
        to_campus_available = []
        for route_time in to_campus_times:
            departure_datetime = datetime.combine(today, route_time)
            is_bookable = now < departure_datetime - timedelta(hours=1)
            
            total_available = 0
            if is_bookable:
                for bus in route_buses:
                    booked_count = sum(1 for b in bookings if b.bus_id == bus.bus_id and b.departure_time == route_time)
                    available_seats = bus.capacity - booked_count
                    total_available += max(0, available_seats)
            
            to_campus_available.append({
                'time': route_time,
                'available_seats': total_available,
                'is_bookable': is_bookable,
                'is_available': total_available > 0 and is_bookable
            })
        
        # Calculate availability for from_campus times
        from_campus_available = []
        for route_time in from_campus_times:
            departure_datetime = datetime.combine(today, route_time)
            is_bookable = now < departure_datetime - timedelta(hours=1)
            
            total_available = 0
            if is_bookable:
                for bus in route_buses:
                    booked_count = sum(1 for b in bookings if b.bus_id == bus.bus_id and b.departure_time == route_time)
                    available_seats = bus.capacity - booked_count
                    total_available += max(0, available_seats)
            
            from_campus_available.append({
                'time': route_time,
                'available_seats': total_available,
                'is_bookable': is_bookable,
                'is_available': total_available > 0 and is_bookable
            })
        
        # Include route with direction-specific times
        routes_with_buses.append({
            'route': route,
            'to_campus_times': to_campus_available,
            'from_campus_times': from_campus_available
        })
    
    return render_template('routes.html', routes_with_buses=routes_with_buses, role=claims['role'], is_admin=(claims['role'] == 'admin'))

@app.route('/my-bookings')
@jwt_required()
def my_bookings():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] == 'student':
        student = Student.query.get(user_id)
        if not student.is_approved:
            flash('Not approved by admin', 'error')
            return redirect(url_for('login'))
        if student.semester_expiry and current_date() >= student.semester_expiry:
            flash('Your semester approval has expired. Please contact admin for renewal.', 'error')
            return redirect(url_for('login'))
    
    # By default show only today's bookings (users commonly visit this page to see today's reservation)
    # Add optional query parameter `all=1` to view all bookings.
    from datetime import datetime
    today = current_date()
    show_all = request.args.get('all', '0').lower() in ('1', 'true', 'yes')

    if show_all:
        bookings = Booking.query.filter_by(student_id=user_id).order_by(Booking.booking_date.desc(), Booking.departure_time).all()
    else:
        bookings = Booking.query.filter_by(student_id=user_id, booking_date=today).order_by(Booking.departure_time).all()
    
    # --- Ensure booking statuses reflect reality ---
    # If a booking's departure datetime has already passed, mark it as 'Traveled'
    from datetime import datetime
    now_dt = datetime.now()
    updated = False
    for b in bookings:
        try:
            dep_dt = datetime.combine(b.booking_date, b.departure_time)
            if b.status != 'Traveled' and dep_dt <= now_dt:
                b.status = 'Traveled'
                updated = True
        except Exception:
            # ignore malformed values
            pass
    if updated:
        db.session.commit()
    # Compute cancellable flag per booking (no cancel within 15 minutes or after departure)
    from datetime import timedelta
    for b in bookings:
        try:
            dep_dt = datetime.combine(b.booking_date, b.departure_time)
            # Default: cannot cancel
            b.can_cancel = False
            if b.status != 'Traveled' and now_dt < dep_dt - timedelta(minutes=15):
                b.can_cancel = True
        except Exception:
            b.can_cancel = False
    
    # Group bookings by date for better display
    bookings_by_date = {}
    for booking in bookings:
        date_key = booking.booking_date
        formatted_date = date_key.strftime('%A, %B %d, %Y')
        if formatted_date not in bookings_by_date:
            bookings_by_date[formatted_date] = []
        bookings_by_date[formatted_date].append(booking)
    
    return render_template('my_bookings.html', bookings_by_date=bookings_by_date, role=claims['role'], is_admin=(claims['role'] == 'admin'), now_dt=now_dt)

@app.route('/book', methods=['POST'])
@jwt_required()
def book():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Allow both students and admins to book
    if claims['role'] not in ['student', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # For students, check approval and status
    if claims['role'] == 'student':
        student = Student.query.get(user_id)
        if not student.is_approved:
            return jsonify({'error': 'Not approved by admin'}), 403
        if student.status != 'active':
            return jsonify({'error': 'Your account is blocked. You cannot book buses.'}), 403
        if student.semester_expiry and current_date() >= student.semester_expiry:
            return jsonify({'error': 'Semester access expired'}), 403

    try:
        route_id = int(request.form['route_id'])
        direction = request.form.get('direction', 'to_campus')
        departure_time_str = request.form.get('departure_time')
        if direction not in ['to_campus', 'from_campus']:
            return jsonify({'error': 'Invalid direction'}), 400
        if not departure_time_str:
            return jsonify({'error': 'Departure time is required'}), 400
        
        # Parse departure time
        from datetime import datetime
        departure_time = datetime.strptime(departure_time_str, '%H:%M').time()
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Missing or invalid form data: {str(e)}'}), 400

    # Enforce special-route booking rules:
    # - Routes named 'Campus ⇄ Banani' and 'Campus ⇄ Gulshan' are restricted: only students who registered
    #   with that route as their preferred_route may book that route.
    # - Students who registered for Banani or Gulshan may book any other routes as well.
    # - Other students may book any non-special routes but cannot book the special ones.
    special_names = ['Campus ⇄ Banani', 'Campus ⇄ Gulshan']
    try:
        requested_route = Route.query.get(route_id)
        special_routes = Route.query.filter(Route.route_name.in_(special_names)).all()
        special_ids = [r.route_id for r in special_routes]
    except Exception:
        requested_route = None
        special_ids = []

    if claims['role'] == 'student':
        # student variable is set above when role == 'student'
        pref = getattr(student, 'preferred_route_id', None)
        # If requesting a special route, ensure student's preferred_route matches that special route
        if route_id in special_ids:
            if pref != route_id:
                return jsonify({'error': 'This route is restricted to students registered for it.'}), 403
        else:
            # requesting a non-special route: allowed for everyone, including students who registered for special routes
            pass

    # TIME RESTRICTIONS
    from datetime import datetime, timedelta
    now = datetime.now()
    today = current_date()
    
    # 1. Only allow booking for today's routes
    booking_date = today  # Always book for today
    
    # 2. Check if booking at least 1 hour before departure
    departure_datetime = datetime.combine(today, departure_time)
    if now >= departure_datetime - timedelta(hours=1):
        return jsonify({'error': 'Bookings must be made at least 1 hour before departure time'}), 400
    
    # 3. Check if the bus hasn't departed yet
    if now >= departure_datetime:
        return jsonify({'error': 'Cannot book seats for buses that have already departed'}), 400

    # Check daily limits (only for students)
    if claims['role'] == 'student':
        daily_count = Booking.query.filter_by(
            student_id=student.student_id,
            booking_date=booking_date,
            direction=direction
        ).count()
        if daily_count >= 1:
            return jsonify({'error': f'Daily limit (1 seat) reached for {direction.replace("_", " ")}'}), 400

    # Find all available buses for the selected route and time
    available_buses = []
    
    buses = Bus.query.filter_by(route_id=route_id, status='active').all()
    for bus in buses:
        booked_count = Booking.query.filter_by(bus_id=bus.bus_id, booking_date=booking_date, departure_time=departure_time).count()
        if booked_count < bus.capacity:
            available_buses.append(bus)
    
    if not available_buses:
        return jsonify({'error': 'No buses available for this route and time'}), 400
    
    # Randomly select one of the available buses
    import random
    selected_bus = random.choice(available_buses)

    # Auto-assign next available seat on the selected bus
    booked_seats = [b.seat_number for b in Booking.query.filter_by(
        bus_id=selected_bus.bus_id,
        booking_date=booking_date,
        departure_time=departure_time
    ).all()]
    
    # Find next available seat
    seat = None
    for i in range(1, selected_bus.capacity + 1):
        if i not in booked_seats:
            seat = i
            break
    
    if seat is None:
        return jsonify({'error': 'No seats available on selected bus'}), 400

    new_booking = Booking(
        student_id=user_id,  # Works for both students and admins
        bus_id=selected_bus.bus_id,
        route_id=route_id,
        seat_number=seat,
        direction=direction,
        departure_time=departure_time
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({
        'message': 'Seat booked successfully!',
        'seat_number': seat,
        'bus_number': selected_bus.bus_number
    })

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
@jwt_required()
def delete_booking(booking_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))

    booking = Booking.query.get(booking_id)
    if not booking or booking.student_id != user_id:
        flash('Booking not found', 'error')
        return redirect(url_for('my_bookings'))

    # Prevent cancellations within 15 minutes of departure or after departure
    from datetime import datetime, timedelta
    try:
        departure_dt = datetime.combine(booking.booking_date, booking.departure_time)
    except Exception:
        # can't parse departure time — be conservative and block cancellation
        flash('Unable to cancel booking due to invalid departure time', 'error')
        return redirect(url_for('my_bookings'))

    now = datetime.now()
    if now >= departure_dt:
        # already departed
        # mark as Traveled if not already
        if booking.status != 'Traveled':
            booking.status = 'Traveled'
            db.session.commit()
        flash('Cannot cancel — the bus has already departed', 'error')
        return redirect(url_for('my_bookings'))

    if now >= departure_dt - timedelta(minutes=15):
        flash('Cancellation window closed: bookings cannot be cancelled within 15 minutes of departure', 'error')
        return redirect(url_for('my_bookings'))

    # Safe to delete
    db.session.delete(booking)
    db.session.commit()
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('my_bookings'))

# --- ADMIN ---
@app.route('/admin/dashboard')
@jwt_required()
def admin_dashboard():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    pending_students = Student.query.filter_by(is_approved=False).all()
    all_students = Student.query.filter_by(is_approved=True).all()
    total_students = Student.query.count()
    total_bookings = Booking.query.count()
    
    # Calculate expiry stats
    today = current_date()
    expired_students = len([s for s in all_students if s.semester_expiry and s.semester_expiry < today])
    expiring_soon = len([s for s in all_students if s.semester_expiry and today <= s.semester_expiry < today + timedelta(days=30)])
    
    return render_template('admin_dashboard.html', 
                         pending=pending_students, 
                         all_students=all_students, 
                         buses=Bus.query.all(), 
                         routes=Route.query.all(), 
                         notices=Notice.query.all(), 
                         name=claims['name'], 
                         total_students=total_students, 
                         total_bookings=total_bookings, 
                         role=claims['role'], 
                         is_admin=True,
                         expired_students=expired_students,
                         expiring_soon=expiring_soon)

@app.route('/admin/manage/students')
@jwt_required()
def manage_students():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    pending_students = Student.query.filter_by(is_approved=False).all()
    all_students = Student.query.filter_by(is_approved=True).all()

    # Compute total booked seats since activation/approved date for each student
    bookings_count_by_student = {}
    for s in all_students:
        # activation_date: prefer approved_date, fallback to registration_date
        if getattr(s, 'approved_date', None):
            activation_date = s.approved_date
        else:
            # registration_date is datetime; use .date()
            activation_date = s.registration_date.date() if s.registration_date else current_date()

        count = Booking.query.filter(Booking.student_id == s.student_id, Booking.booking_date >= activation_date).count()
        bookings_count_by_student[s.student_id] = count

    routes = Route.query.all()
    return render_template('manage_students.html', pending=pending_students, all_students=all_students, name=claims['name'], current_date=current_date(), bookings_count_by_student=bookings_count_by_student, routes=routes)

@app.route('/admin/manage/buses')
@jwt_required()
def manage_buses():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    buses = Bus.query.order_by(Bus.route_id).all()
    routes = Route.query.all()
    return render_template('manage_buses.html', buses=buses, routes=routes, name=claims['name'])

@app.route('/admin/manage/routes')
@jwt_required()
def manage_routes():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    routes = Route.query.all()
    return render_template('manage_routes.html', routes=routes, name=claims['name'])

@app.route('/admin/manage/notices')
@jwt_required()
def manage_notices():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    notices = Notice.query.all()
    return render_template('manage_notices.html', notices=notices, name=claims['name'])

@app.route('/admin/approve/<int:student_id>')
@jwt_required()
def approve(student_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    if student:
        student.is_approved = True
        # Activate the student for booking upon approval
        student.status = 'active'
        # Only set expiry if not already set (preserves registration expiry)
        if not student.semester_expiry:
            student.semester_expiry = current_date() + timedelta(days=120)
        # set approved_date when approving
        if not getattr(student, 'approved_date', None):
            student.approved_date = current_date()
        db.session.commit()
        flash('Student approved!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/reject/<int:student_id>')
@jwt_required()
def reject(student_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Student rejected and removed!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/renew_student/<int:student_id>')
@jwt_required()
def renew_student(student_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    if student:
        from datetime import datetime, timedelta
        # Extend expiry by 4 months from current expiry date
        if student.semester_expiry:
            student.semester_expiry = student.semester_expiry + timedelta(days=120)
        else:
            student.semester_expiry = current_date() + timedelta(days=120)
        db.session.commit()
        flash('Student approval renewed for another 4 months!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/student/add', methods=['POST'])
@jwt_required()
def add_student():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    student = Student(
        name=request.form['name'],
        email=request.form['email'],
        password=hash_password(request.form['password']),
        is_approved=True,
        approved_date=current_date(),
        status='active'
    )
    db.session.add(student)
    db.session.commit()
    flash('Student added successfully!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/bus/add', methods=['POST'])
@jwt_required()
def add_bus():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    bus = Bus(
        bus_number=request.form['bus_number'],
        driver_name=request.form['driver_name'],
        capacity=int(request.form['capacity']),
        route_id=int(request.form['route_id']) if request.form.get('route_id') else None,
        status='active'
    )
    db.session.add(bus)
    db.session.commit()
    flash('Bus added successfully!', 'success')
    return redirect(url_for('manage_buses'))

@app.route('/admin/bus/edit/<int:bus_id>', methods=['POST'])
@jwt_required()
def edit_bus(bus_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    bus = Bus.query.get(bus_id)
    if not bus:
        flash('Bus not found', 'error')
        return redirect(url_for('manage_buses'))
    
    bus.bus_number = request.form['bus_number']
    bus.driver_name = request.form['driver_name']
    bus.capacity = int(request.form['capacity'])
    bus.route_id = int(request.form['route_id']) if request.form.get('route_id') else None
    db.session.commit()
    flash('Bus updated successfully!', 'success')
    return redirect(url_for('manage_buses'))

@app.route('/admin/route/add', methods=['POST'])
@jwt_required()
def add_route():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    route = Route(
        route_name=request.form['route_name'],
        start_point=request.form['start_point'],
        end_point=request.form['end_point'],
        distance=float(request.form['distance']),
        duration=int(request.form['duration']),
        status='active'
    )
    db.session.add(route)
    db.session.commit()
    flash('Route added successfully!', 'success')
    return redirect(url_for('manage_routes'))

@app.route('/admin/route/edit/<int:route_id>', methods=['POST'])
@jwt_required()
def edit_route(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    route = Route.query.get(route_id)
    if not route:
        flash('Route not found', 'error')
        return redirect(url_for('manage_routes'))
    
    route.route_name = request.form['route_name']
    route.start_point = request.form['start_point']
    route.end_point = request.form['end_point']
    route.distance = float(request.form['distance'])
    route.duration = int(request.form['duration'])
    db.session.commit()
    flash('Route updated successfully!', 'success')
    return redirect(url_for('manage_routes'))

@app.route('/admin/route/times/<int:route_id>')
@jwt_required()
def get_route_times(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    route = Route.query.get(route_id)
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    times = route.get_departure_times()
    return jsonify({'times': [t.strftime('%H:%M') for t in times]})

@app.route('/admin/route/times/add/<int:route_id>', methods=['POST'])
@jwt_required()
def add_route_time(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    route = Route.query.get(route_id)
    if not route:
        flash('Route not found', 'error')
        return redirect(url_for('manage_routes'))
    
    new_time_str = request.form.get('new_time')
    if not new_time_str:
        flash('Time is required', 'error')
        return redirect(url_for('manage_routes'))
    
    from datetime import datetime
    try:
        new_time = datetime.strptime(new_time_str, '%H:%M').time()
    except ValueError:
        flash('Invalid time format', 'error')
        return redirect(url_for('manage_routes'))
    
    current_times = route.get_departure_times()
    if new_time in current_times:
        flash('Time already exists', 'warning')
        return redirect(url_for('manage_routes'))
    
    current_times.append(new_time)
    route.set_departure_times(current_times)
    db.session.commit()
    flash('Departure time added successfully!', 'success')
    return redirect(url_for('manage_routes'))

@app.route('/admin/route/times/delete/<int:route_id>', methods=['POST'])
@jwt_required()
def delete_route_time(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    route = Route.query.get(route_id)
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    time_str = request.form.get('time')
    if not time_str:
        return jsonify({'error': 'Time is required'}), 400
    
    from datetime import datetime
    try:
        time_to_delete = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid time format'}), 400
    
    current_times = route.get_departure_times()
    if time_to_delete not in current_times:
        return jsonify({'error': 'Time not found'}), 404
    
    current_times.remove(time_to_delete)
    route.set_departure_times(current_times)
    db.session.commit()
    return jsonify({'message': 'Time deleted successfully'})

@app.route('/admin/notice/add', methods=['POST'])
@jwt_required()
def add_notice():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    notice = Notice(
        title=request.form['title'],
        content=request.form['content'],
        posted_date=datetime.utcnow(),
        status='active'
    )
    db.session.add(notice)
    db.session.commit()
    flash('Notice added successfully!', 'success')
    return redirect(url_for('manage_notices'))

@app.route('/admin/notice/edit/<int:notice_id>', methods=['POST'])
@jwt_required()
def edit_notice(notice_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    
    notice = Notice.query.get(notice_id)
    if not notice:
        flash('Notice not found', 'error')
        return redirect(url_for('manage_notices'))
    
    notice.title = request.form['title']
    notice.content = request.form['content']
    db.session.commit()
    flash('Notice updated successfully!', 'success')
    return redirect(url_for('manage_notices'))

@app.route('/admin/semester/clear')
@jwt_required()
def semester_clear():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    Booking.query.delete()
    Student.query.update({'is_approved': False})
    notice = Notice(
        title="New Semester Started!",
        content="All transport access has been reset. Please re-register.",
        posted_date=datetime.utcnow(),
        status='active'
    )
    db.session.add(notice)
    db.session.commit()
    flash('Semester cleared!', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_student_status/<int:student_id>/<status>')
@jwt_required()
def toggle_student_status(student_id, status):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    if student:
        student.status = status
        db.session.commit()
        flash(f'Student status updated to {status}!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/toggle_bus_status/<int:bus_id>/<status>')
@jwt_required()
def toggle_bus_status(bus_id, status):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    bus = Bus.query.get(bus_id)
    if bus:
        bus.status = status
        db.session.commit()
        flash(f'Bus status updated to {status}!', 'success')
    return redirect(url_for('manage_buses'))

@app.route('/admin/toggle_route_status/<int:route_id>/<status>')
@jwt_required()
def toggle_route_status(route_id, status):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    route = Route.query.get(route_id)
    if route:
        route.status = status
        db.session.commit()
        flash(f'Route status updated to {status}!', 'success')
    return redirect(url_for('manage_routes'))

@app.route('/admin/toggle_notice_status/<int:notice_id>/<status>')
@jwt_required()
def toggle_notice_status(notice_id, status):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(notice_id)
    if notice:
        notice.status = status
        db.session.commit()
        flash(f'Notice status updated to {status}!', 'success')
    return redirect(url_for('manage_notices'))

@app.route('/admin/delete_student/<int:student_id>')
@jwt_required()
def delete_student(student_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(student_id)
    if student:
        # Delete associated bookings first
        Booking.query.filter_by(student_id=student_id).delete()
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    return redirect(url_for('manage_students'))

@app.route('/admin/delete_bus/<int:bus_id>')
@jwt_required()
def delete_bus(bus_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    bus = Bus.query.get(bus_id)
    if bus:
        # Delete associated bookings first
        Booking.query.filter_by(bus_id=bus_id).delete()
        db.session.delete(bus)
        db.session.commit()
        flash('Bus deleted successfully!', 'success')
    return redirect(url_for('manage_buses'))

@app.route('/admin/delete_route/<int:route_id>')
@jwt_required()
def delete_route(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    route = Route.query.get(route_id)
    if route:
        # Delete associated bookings and notices first
        Booking.query.filter_by(route_id=route_id).delete()
        Notice.query.filter_by(route_id=route_id).delete()
        db.session.delete(route)
        db.session.commit()
        flash('Route deleted successfully!', 'success')
    return redirect(url_for('manage_routes'))

@app.route('/admin/delete_notice/<int:notice_id>')
@jwt_required()
def delete_notice(notice_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(notice_id)
    if notice:
        db.session.delete(notice)
        db.session.commit()
        flash('Notice deleted successfully!', 'success')
    return redirect(url_for('manage_notices'))

# --- API ENDPOINTS ---

@app.route('/api/routes')
@jwt_required()
def api_routes():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    routes = Route.query.filter_by(status='active').all()
    return jsonify([{
        'route_id': route.route_id,
        'route_name': route.route_name,
        'start_point': route.start_point,
        'end_point': route.end_point,
        'distance': route.distance,
        'duration': route.duration
    } for route in routes])

@app.route('/api/buses/<int:route_id>')
@jwt_required()
def api_buses(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    buses = Bus.query.filter_by(route_id=route_id, status='active').all()
    buses_data = []
    
    today = current_date()
    for bus in buses:
        booked_count = Booking.query.filter_by(bus_id=bus.bus_id, booking_date=today).count()
        available_seats = bus.capacity - booked_count
        
        buses_data.append({
            'bus': {
                'bus_id': bus.bus_id,
                'bus_number': bus.bus_number,
                'driver_name': bus.driver_name,
                'capacity': bus.capacity,
                'route_id': bus.route_id,
                'start_time': bus.start_time.strftime('%H:%M') if bus.start_time else None,
                'status': bus.status
            },
            'available_seats': available_seats
        })
    
    return jsonify({'buses': buses_data})

@app.route('/api/times/<int:route_id>')
@jwt_required()
def api_times(route_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    buses = Bus.query.filter_by(route_id=route_id, status='active').all()
    times = set()
    
    for bus in buses:
        if bus.start_time:
            times.add(bus.start_time.strftime('%H:%M'))
    
    return jsonify({'times': sorted(list(times))})

@app.route('/api/bookings')
@jwt_required()
def api_bookings():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    bookings = Booking.query.filter_by(student_id=user_id).all()
    bookings_data = []
    
    for booking in bookings:
        bus = Bus.query.get(booking.bus_id)
        route = Route.query.get(booking.route_id)
        
        bookings_data.append({
            'booking_id': booking.booking_id,
            'student_id': booking.student_id,
            'bus_id': booking.bus_id,
            'route_id': booking.route_id,
            'seat_number': booking.seat_number,
            'direction': booking.direction,
            'departure_time': booking.departure_time.strftime('%H:%M') if booking.departure_time else None,
            'status': booking.status,
            'booking_date': booking.booking_date.isoformat(),
            'bus': {
                'bus_id': bus.bus_id,
                'bus_number': bus.bus_number,
                'driver_name': bus.driver_name,
                'capacity': bus.capacity
            },
            'route': {
                'route_id': route.route_id,
                'route_name': route.route_name,
                'start_point': route.start_point,
                'end_point': route.end_point
            }
        })
    
    return jsonify(bookings_data)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5001)