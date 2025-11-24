from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_date = db.Column(db.Date)
    # Optional fields for registration flow
    department = db.Column(db.String(100))
    student_number = db.Column(db.String(50))
    payment_receipt_id = db.Column(db.String(100))
    preferred_route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active, blocked, pending
    semester_expiry = db.Column(db.Date)
    bookings = db.relationship('Booking', backref='student')

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Bus(db.Model):
    __tablename__ = 'buses'
    bus_id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(50), nullable=False)
    driver_name = db.Column(db.String(100))
    # Optional start_time for this bus (time of departure)
    start_time = db.Column(db.Time, nullable=True)
    capacity = db.Column(db.Integer, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive
    bookings = db.relationship('Booking', backref='bus')
    route = db.relationship('Route')

class Route(db.Model):
    __tablename__ = 'routes'
    route_id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    start_point = db.Column(db.String(100))
    end_point = db.Column(db.String(100))
    distance = db.Column(db.Float)
    duration = db.Column(db.Integer)  # in minutes
    departure_times = db.Column(db.Text, default='[]')  # JSON array of time strings like ["08:00", "09:30", "14:00"]
    status = db.Column(db.String(20), default='active')  # active, inactive
    bookings = db.relationship('Booking', backref='route')
    notices = db.relationship('Notice')
    buses = db.relationship('Bus')

    def get_departure_times(self):
        """Get departure times as list of time objects"""
        try:
            times_str = json.loads(self.departure_times or '[]')
            from datetime import datetime
            return [datetime.strptime(t, '%H:%M').time() for t in times_str]
        except:
            return []

    def set_departure_times(self, times):
        """Set departure times from list of time objects or strings"""
        if not times:
            self.departure_times = '[]'
            return
        
        times_str = []
        for t in times:
            if isinstance(t, str):
                times_str.append(t)
            else:
                times_str.append(t.strftime('%H:%M'))
        
        self.departure_times = json.dumps(sorted(times_str))

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    direction = db.Column(db.String(20), nullable=False, default='to_campus')  # to_campus, from_campus
    departure_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')
    booking_date = db.Column(db.Date, default=datetime.utcnow().date)

class Notice(db.Model):
    __tablename__ = 'notices'
    notice_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, inactive
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=True)
    route = db.relationship('Route')