# DUTP - Comprehensive DBMS Analysis & Implementation Documentation

## Table of Contents
1. [Database Architecture Overview](#database-architecture-overview)
2. [Entity-Relationship Model](#entity-relationship-model)
3. [Normalization Analysis](#normalization-analysis)
4. [Table Schemas with Constraints](#table-schemas-with-constraints)
5. [Relationships & Foreign Keys](#relationships--foreign-keys)
6. [Indexing Strategy](#indexing-strategy)
7. [Transactions & ACID Properties](#transactions--acid-properties)
8. [Query Optimization](#query-optimization)
9. [Data Integrity Mechanisms](#data-integrity-mechanisms)
10. [Concurrency Control](#concurrency-control)

---

## 1. Database Architecture Overview

### Database Management System: SQLite
- **Type**: Relational Database Management System (RDBMS)
- **Architecture**: Embedded, serverless, zero-configuration
- **Storage Engine**: Single file database (`dutp.db`)
- **Transaction Support**: Full ACID compliance
- **Concurrency**: File-level locking

### ORM Layer: SQLAlchemy
- **Pattern**: Active Record + Data Mapper
- **Connection Pooling**: Managed by Flask-SQLAlchemy
- **Migration Support**: Not implemented (uses `db.create_all()`)
- **Lazy Loading**: Default for relationships

### Database Schema Statistics
```
Total Tables: 6
  - Students (User Accounts)
  - Admins (Administrative Accounts)
  - Routes (Transport Routes)
  - Buses (Transport Vehicles)
  - Bookings (Reservation Records)
  - Notices (Announcements)

Total Relationships: 7
Total Foreign Keys: 5
Primary Keys: 6 (one per table)
```

---

## 2. Entity-Relationship Model

### Enhanced ER Diagram (Chen Notation)

```
                    ┌─────────────┐
                    │   STUDENT   │
                    └──────┬──────┘
                           │ 1
                           │
                           │ (makes)
                           │
                           │ M
                    ┌──────▼──────┐
                    │   BOOKING   │
                    └──────┬──────┘
                           │ M
                           │
              ┌────────────┼────────────┐
              │            │            │
              │ M          │ M          │ M
              │            │            │
       ┌──────▼──────┐    │     ┌──────▼──────┐
       │     BUS     │    │     │    ROUTE    │
       └──────┬──────┘    │     └──────┬──────┘
              │ M         │            │ 1
              │           │            │
              │ (assigned)│            │ (posts)
              │           │            │
              │ 1         │            │ M
       ┌──────▼──────┐    │     ┌──────▼──────┐
       │    ROUTE    │    │     │   NOTICE    │
       └─────────────┘    │     └─────────────┘
                          │ M
                   ┌──────▼──────┐
                   │    ROUTE    │
                   └─────────────┘

       ADMIN (manages all entities)
```

### Cardinality Mapping

| Relationship | Cardinality | Type | Participation |
|-------------|-------------|------|---------------|
| Student → Booking | 1:M | One-to-Many | Partial (student may have 0 bookings) |
| Bus → Booking | 1:M | One-to-Many | Partial (bus may have 0 bookings) |
| Route → Booking | 1:M | One-to-Many | Partial (route may have 0 bookings) |
| Route → Bus | 1:M | One-to-Many | Partial (route may have 0 buses) |
| Route → Notice | 1:M | One-to-Many | Partial (route may have 0 notices) |
| Student → Route | M:1 | Many-to-One | Partial (preferred route is optional) |

---

## 3. Normalization Analysis

### First Normal Form (1NF) ✓

**Definition**: Each column contains atomic values, no repeating groups.

**Analysis**:

✓ **Students Table**:
- All attributes are atomic (student_id, name, email, etc.)
- No multi-valued attributes
- Each column has single value per row

✓ **Routes Table** - **EXCEPTION HANDLED**:
```python
departure_times = db.Column(db.Text, default='[]')  # Stored as JSON
```
**Issue**: `departure_times` appears to violate 1NF (stores array as JSON)

**Justification**:
- Treated as single TEXT value at database level
- Application layer handles parsing (via `get_departure_times()`)
- Alternative would require separate DepartureTimes table

**Normalized Alternative** (not implemented):
```sql
CREATE TABLE departure_times (
    id INTEGER PRIMARY KEY,
    route_id INTEGER FOREIGN KEY,
    time TIME,
    UNIQUE(route_id, time)
);
```

✓ **Other Tables**: All in 1NF

---

### Second Normal Form (2NF) ✓

**Definition**: In 1NF + No partial dependencies (non-key attributes fully depend on entire primary key)

**Analysis**:

✓ **All tables use single-column primary keys**:
- Students: `student_id`
- Admins: `admin_id`
- Buses: `bus_id`
- Routes: `route_id`
- Bookings: `booking_id`
- Notices: `notice_id`

**Conclusion**: No partial dependencies possible with single-column PKs. All tables are in 2NF.

---

### Third Normal Form (3NF) ✓

**Definition**: In 2NF + No transitive dependencies (non-key attributes don't depend on other non-key attributes)

**Analysis**:

**Students Table**:
```python
student_id → name, email, department, ...
student_id → preferred_route_id
preferred_route_id → route_name (in Routes table)
```
- No transitive dependency because `route_name` is not stored in Students
- Foreign key relationship properly implemented ✓

**Buses Table**:
```python
bus_id → bus_number, driver_name, capacity, route_id
route_id → route_name, start_point, ... (in Routes table)
```
- Route details stored in separate Routes table ✓
- No transitive dependencies ✓

**Bookings Table**:
```python
booking_id → student_id, bus_id, route_id, seat_number, ...
```
- All foreign keys point to separate tables ✓
- Student details in Students table
- Bus details in Buses table
- Route details in Routes table
- No transitive dependencies ✓

**Conclusion**: All tables are in 3NF.

---

### Boyce-Codd Normal Form (BCNF) ✓

**Definition**: In 3NF + Every determinant is a candidate key

**Analysis**:

All tables have:
- Single primary key as only candidate key
- No other determinants
- All non-key attributes depend solely on PK

**Conclusion**: All tables are in BCNF.

---

### Denormalization Decisions

**1. Booking Table - Redundant route_id**

```python
class Booking(db.Model):
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id'))
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'))
```

**Issue**: `route_id` can be derived from `bus_id` (via Bus → Route relationship)

**Justification**:
- **Query Performance**: Direct access to route without JOIN
- **Data Integrity**: Explicit constraint ensures bus and route match
- **Read Optimization**: Bookings are queried frequently by route
- **Trade-off**: Storage vs. Query Speed (acceptable for small dataset)

**Alternative Normalized Query** (slower):
```sql
SELECT * FROM bookings b
JOIN buses bu ON b.bus_id = bu.bus_id
WHERE bu.route_id = ?
```

**Current Query** (faster):
```sql
SELECT * FROM bookings WHERE route_id = ?
```

---

## 4. Table Schemas with Constraints

### Students Table

```sql
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_date DATE,
    department VARCHAR(100),
    student_number VARCHAR(50),
    payment_receipt_id VARCHAR(100),
    preferred_route_id INTEGER,
    is_approved BOOLEAN DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    semester_expiry DATE,
    
    CONSTRAINT fk_student_route 
        FOREIGN KEY (preferred_route_id) 
        REFERENCES routes(route_id)
        ON DELETE SET NULL,
    
    CONSTRAINT chk_status 
        CHECK (status IN ('active', 'blocked', 'pending')),
    
    CONSTRAINT chk_email_format
        CHECK (email LIKE '%@%')
);
```

**Constraints Analysis**:
- **PRIMARY KEY**: Ensures uniqueness, auto-increment
- **NOT NULL**: Mandatory fields (name, email, password)
- **UNIQUE**: Prevents duplicate emails
- **FOREIGN KEY**: Links to Routes table
- **CHECK**: Validates status values
- **DEFAULT**: Auto-populates registration_date, is_approved, status

**Indexes** (automatic):
- PRIMARY KEY creates clustered index on `student_id`
- UNIQUE creates index on `email`

---

### Admins Table

```sql
CREATE TABLE admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    
    CONSTRAINT chk_admin_email
        CHECK (email LIKE '%@%')
);
```

**Constraints Analysis**:
- Minimal structure for security
- Email uniqueness prevents duplicate admin accounts
- No relationship to other tables (deliberate isolation)

---

### Routes Table

```sql
CREATE TABLE routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_name VARCHAR(100) NOT NULL,
    start_point VARCHAR(100),
    end_point VARCHAR(100),
    distance FLOAT,
    duration INTEGER,  -- in minutes
    departure_times TEXT DEFAULT '[]',  -- JSON array
    status VARCHAR(20) DEFAULT 'active',
    
    CONSTRAINT chk_route_status
        CHECK (status IN ('active', 'inactive')),
    
    CONSTRAINT chk_distance
        CHECK (distance IS NULL OR distance > 0),
    
    CONSTRAINT chk_duration
        CHECK (duration IS NULL OR duration > 0)
);
```

**Constraints Analysis**:
- **CHECK on distance/duration**: Ensures positive values
- **DEFAULT '[]'**: Empty JSON array for no departure times
- **JSON Storage**: Trade-off between normalization and flexibility

**JSON Field Structure**:
```json
["09:00", "14:00", "18:00"]
```

---

### Buses Table

```sql
CREATE TABLE buses (
    bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_number VARCHAR(50) NOT NULL,
    driver_name VARCHAR(100),
    start_time TIME,
    capacity INTEGER NOT NULL,
    route_id INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    
    CONSTRAINT fk_bus_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE,
    
    CONSTRAINT chk_bus_status
        CHECK (status IN ('active', 'inactive')),
    
    CONSTRAINT chk_capacity
        CHECK (capacity > 0 AND capacity <= 100),
    
    CONSTRAINT uq_bus_number
        UNIQUE (bus_number)
);
```

**Constraints Analysis**:
- **CASCADE DELETE**: When route deleted, buses are also deleted
- **Capacity Validation**: Reasonable limits (1-100 seats)
- **Unique Bus Number**: Prevents duplicate bus identifiers

---

### Bookings Table

```sql
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    bus_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,
    direction VARCHAR(20) NOT NULL DEFAULT 'to_campus',
    departure_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'Booked',
    booking_date DATE DEFAULT CURRENT_DATE,
    
    CONSTRAINT fk_booking_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_booking_bus
        FOREIGN KEY (bus_id)
        REFERENCES buses(bus_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_booking_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE,
    
    CONSTRAINT chk_direction
        CHECK (direction IN ('to_campus', 'from_campus')),
    
    CONSTRAINT chk_booking_status
        CHECK (status IN ('Booked', 'Cancelled', 'Completed')),
    
    CONSTRAINT chk_seat_number
        CHECK (seat_number > 0),
    
    CONSTRAINT uq_booking_seat
        UNIQUE (bus_id, seat_number, departure_time, booking_date, direction)
);
```

**Constraints Analysis**:

**Referential Integrity**:
- **CASCADE DELETE**: When student/bus/route deleted, bookings automatically deleted
- Maintains database consistency

**Business Logic Constraints**:
- **UNIQUE Composite Key**: Prevents double-booking same seat
  ```
  (bus_id, seat_number, departure_time, booking_date, direction)
  ```
  - Same seat can be booked for different times ✓
  - Same seat can be booked for different dates ✓
  - Same seat can be booked for different directions ✓
  - Same seat CANNOT be booked twice for same (bus, time, date, direction) ✗

**Example Scenarios**:

✓ **Valid**: 
```sql
Booking 1: bus=1, seat=5, time=09:00, date=2025-12-04, dir=to_campus
Booking 2: bus=1, seat=5, time=14:00, date=2025-12-04, dir=to_campus (Different time)
```

✓ **Valid**:
```sql
Booking 1: bus=1, seat=5, time=09:00, date=2025-12-04, dir=to_campus
Booking 2: bus=1, seat=5, time=09:00, date=2025-12-04, dir=from_campus (Different direction)
```

✗ **Invalid** (Constraint Violation):
```sql
Booking 1: bus=1, seat=5, time=09:00, date=2025-12-04, dir=to_campus
Booking 2: bus=1, seat=5, time=09:00, date=2025-12-04, dir=to_campus (Duplicate)
```

---

### Notices Table

```sql
CREATE TABLE notices (
    notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(150),
    content TEXT,
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    route_id INTEGER,
    
    CONSTRAINT fk_notice_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE SET NULL,
    
    CONSTRAINT chk_notice_status
        CHECK (status IN ('active', 'inactive'))
);
```

**Constraints Analysis**:
- **SET NULL on route deletion**: Notice remains but loses route association
- **Optional route_id**: Allows general notices (NULL = all routes)

---

## 5. Relationships & Foreign Keys

### Foreign Key Cascade Rules

| Table | Foreign Key | On Delete | On Update | Justification |
|-------|-------------|-----------|-----------|---------------|
| Students | preferred_route_id | SET NULL | CASCADE | Route deletion shouldn't delete students, just clear preference |
| Buses | route_id | CASCADE | CASCADE | Bus without route has no purpose, delete it |
| Bookings | student_id | CASCADE | CASCADE | Student deletion should cancel all their bookings |
| Bookings | bus_id | CASCADE | CASCADE | Bus deletion should cancel all bookings on it |
| Bookings | route_id | CASCADE | CASCADE | Route deletion should cancel all bookings for it |
| Notices | route_id | SET NULL | CASCADE | Notice becomes general when route deleted |

### Relationship Implementation

**One-to-Many: Student → Bookings**
```python
class Student(db.Model):
    bookings = db.relationship('Booking', backref='student')

class Booking(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
```

**ORM Translation**:
```python
# Access student's bookings
student = Student.query.get(1)
student.bookings  # Returns list of Booking objects

# Access booking's student (via backref)
booking = Booking.query.get(1)
booking.student  # Returns Student object
```

**SQL Equivalent**:
```sql
-- Get student's bookings
SELECT * FROM bookings WHERE student_id = 1;

-- Get booking's student
SELECT s.* FROM students s
JOIN bookings b ON s.student_id = b.student_id
WHERE b.booking_id = 1;
```

**Lazy Loading**:
```python
student.bookings  # Triggers: SELECT * FROM bookings WHERE student_id = ?
```

---

## 6. Indexing Strategy

### Automatic Indexes

**SQLAlchemy creates indexes automatically for**:

1. **Primary Keys** (Clustered Indexes):
   - students(student_id)
   - admins(admin_id)
   - routes(route_id)
   - buses(bus_id)
   - bookings(booking_id)
   - notices(notice_id)

2. **Unique Constraints** (Non-clustered Indexes):
   - students(email)
   - admins(email)
   - buses(bus_number)
   - bookings(bus_id, seat_number, departure_time, booking_date, direction)

3. **Foreign Keys** (Automatically indexed in SQLite):
   - students(preferred_route_id)
   - buses(route_id)
   - bookings(student_id)
   - bookings(bus_id)
   - bookings(route_id)
   - notices(route_id)

### Recommended Additional Indexes (Not Implemented)

```sql
-- Frequently queried by date
CREATE INDEX idx_bookings_date ON bookings(booking_date);

-- Admin filtering by status
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_approved ON students(is_approved);

-- Student dashboard queries
CREATE INDEX idx_bookings_student_date 
ON bookings(student_id, booking_date);

-- Route filtering
CREATE INDEX idx_buses_route ON buses(route_id);

-- Composite index for common query
CREATE INDEX idx_bookings_lookup 
ON bookings(route_id, booking_date, departure_time);
```

### Index Performance Analysis

**Query**: Find today's bookings for a student
```python
Booking.query.filter_by(
    student_id=student_id,
    booking_date=today
).all()
```

**Without Index**:
```
Full table scan: O(n) where n = total bookings
```

**With Index on (student_id, booking_date)**:
```
B-tree lookup: O(log n) + sequential scan of matching rows
```

---

## 7. Transactions & ACID Properties

### ACID Compliance in SQLite

#### Atomicity ✓
**Implementation**: Write-Ahead Logging (WAL)

**Example Transaction**:
```python
try:
    db.session.add(booking)
    db.session.commit()  # All or nothing
except:
    db.session.rollback()  # Undo all changes
```

**Scenario**: Student books multiple seats
```python
try:
    booking1 = Booking(student_id=1, seat_number=5, ...)
    booking2 = Booking(student_id=1, seat_number=6, ...)
    db.session.add(booking1)
    db.session.add(booking2)
    db.session.commit()  # Both succeed or both fail
except IntegrityError:
    db.session.rollback()  # Neither booking is saved
```

#### Consistency ✓
**Implementation**: Constraint enforcement

**Constraints Enforced**:
- Foreign key constraints
- Unique constraints
- Check constraints
- NOT NULL constraints

**Example**:
```python
# Attempt to book already-booked seat
booking = Booking(
    bus_id=1, 
    seat_number=5,  # Already booked
    departure_time='09:00',
    booking_date='2025-12-04',
    direction='to_campus'
)
db.session.add(booking)
db.session.commit()  # Raises IntegrityError
```

#### Isolation ✓
**Level**: Serializable (SQLite default)

**Implementation**: Database-level locking

**Concurrency Scenarios**:

**Scenario 1**: Two students booking same seat simultaneously
```
Time | Student A                    | Student B
-----|------------------------------|-----------------------------
T1   | SELECT seat 5 availability   | 
T2   |                              | SELECT seat 5 availability
T3   | INSERT booking (seat 5)      |
T4   | COMMIT                       |
T5   |                              | INSERT booking (seat 5)
T6   |                              | ROLLBACK (unique violation)
```

**Scenario 2**: Admin editing route while student viewing routes
```
Time | Admin                        | Student
-----|------------------------------|-----------------------------
T1   | BEGIN TRANSACTION            |
T2   | UPDATE routes SET ...        |
T3   |                              | SELECT * FROM routes
T4   |                              | (Waits for admin commit)
T5   | COMMIT                       |
T6   |                              | (Gets updated data)
```

#### Durability ✓
**Implementation**: Write-Ahead Log (WAL) + fsync

**Mechanism**:
1. Changes written to WAL file
2. WAL synced to disk (fsync)
3. Checkpoint: WAL changes merged to main database
4. Even if system crashes, WAL recovers committed transactions

---

## 8. Query Optimization

### Common Query Patterns

#### 1. Student Dashboard - Today's Bookings

**Unoptimized Query**:
```python
bookings = Booking.query.filter_by(student_id=student_id).all()
bookings_today = [b for b in bookings if b.booking_date == today]
```
**Issues**:
- Fetches all bookings from database
- Filters in Python (memory intensive)
- O(n) where n = total student bookings

**Optimized Query**:
```python
bookings = Booking.query.filter_by(
    student_id=student_id,
    booking_date=today
).all()
```
**Benefits**:
- Database filters before returning results
- Uses index on student_id
- O(log n) lookup + O(k) where k = today's bookings

**SQL Generated**:
```sql
SELECT * FROM bookings 
WHERE student_id = ? AND booking_date = ?
```

---

#### 2. Available Seats Query

**Current Implementation** (app.py):
```python
bus = Bus.query.get(bus_id)
booked_seats = Booking.query.filter_by(
    bus_id=bus_id,
    departure_time=departure_time,
    booking_date=datetime.utcnow().date(),
    direction=direction,
    status='Booked'
).all()
booked_seat_numbers = [b.seat_number for b in booked_seats]
available_seats = [i for i in range(1, bus.capacity + 1) 
                   if i not in booked_seat_numbers]
```

**Query Cost**:
- 1 query for bus details
- 1 query for booked seats
- Python list comprehension for available seats

**Optimized SQL Approach** (not implemented):
```sql
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n+1 FROM numbers WHERE n < (SELECT capacity FROM buses WHERE bus_id = ?)
)
SELECT n AS available_seat
FROM numbers
WHERE n NOT IN (
    SELECT seat_number FROM bookings
    WHERE bus_id = ? 
    AND departure_time = ?
    AND booking_date = ?
    AND direction = ?
    AND status = 'Booked'
)
```

---

#### 3. Admin Pending Students

**Current Query**:
```python
pending = Student.query.filter_by(is_approved=False).all()
```

**SQL**:
```sql
SELECT * FROM students WHERE is_approved = 0
```

**Optimization**:
- Index on `is_approved` column would speed up filtering
- Add `LIMIT` for pagination

**With Pagination**:
```python
pending = Student.query.filter_by(is_approved=False)\
                       .paginate(page=1, per_page=20)
```

---

#### 4. Route Buses Query

**N+1 Query Problem**:
```python
routes = Route.query.all()
for route in routes:
    buses = route.buses  # Triggers separate query for each route!
```

**SQL Generated** (N+1 queries):
```sql
SELECT * FROM routes;  -- 1 query
SELECT * FROM buses WHERE route_id = 1;  -- Query 2
SELECT * FROM buses WHERE route_id = 2;  -- Query 3
-- ... N more queries
```

**Optimized with Eager Loading**:
```python
from sqlalchemy.orm import joinedload
routes = Route.query.options(joinedload(Route.buses)).all()
```

**SQL Generated** (1 query):
```sql
SELECT routes.*, buses.* 
FROM routes 
LEFT JOIN buses ON routes.route_id = buses.route_id
```

---

### Query Execution Plans

**SQLite EXPLAIN QUERY PLAN**:

**Query**: Find student bookings
```sql
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE student_id = 5;
```

**Without Index**:
```
SCAN TABLE bookings
```
Time: O(n)

**With Index**:
```
SEARCH TABLE bookings USING INDEX idx_bookings_student (student_id=?)
```
Time: O(log n)

---

## 9. Data Integrity Mechanisms

### Entity Integrity

**Primary Key Constraints**:
- Every table has a primary key
- Auto-increment ensures uniqueness
- NOT NULL implicitly enforced

**Example**:
```python
student = Student(name="John", email="john@example.com")
db.session.add(student)
db.session.commit()
# student.student_id automatically assigned (e.g., 42)
```

---

### Referential Integrity

**Foreign Key Constraints**:

**Example 1: Prevent Orphaned Bookings**
```python
# Attempt to create booking with non-existent student
booking = Booking(
    student_id=9999,  # Doesn't exist
    bus_id=1,
    route_id=1,
    seat_number=5
)
db.session.add(booking)
db.session.commit()  # Raises IntegrityError: FOREIGN KEY constraint failed
```

**Example 2: Cascade Delete**
```python
# Delete student
student = Student.query.get(1)
db.session.delete(student)
db.session.commit()
# All bookings with student_id=1 automatically deleted
```

**Example 3: Set NULL**
```python
# Delete route
route = Route.query.get(5)
db.session.delete(route)
db.session.commit()
# Students with preferred_route_id=5 now have preferred_route_id=NULL
```

---

### Domain Integrity

**Check Constraints**:

**1. Status Validation**:
```python
student = Student(name="John", email="john@ex.com", status="invalid")
db.session.add(student)
db.session.commit()  
# Raises: CHECK constraint failed: status IN ('active', 'blocked', 'pending')
```

**2. Capacity Validation**:
```python
bus = Bus(bus_number="B123", capacity=150)  # Exceeds 100
db.session.add(bus)
db.session.commit()
# Raises: CHECK constraint failed: capacity <= 100
```

**3. Email Format Validation**:
```python
student = Student(name="John", email="invalid-email")
db.session.add(student)
db.session.commit()
# Raises: CHECK constraint failed: email LIKE '%@%'
```

---

### Business Rule Integrity

**Implemented in Application Layer** (not database constraints):

**1. Semester Expiry Check**:
```python
# app.py - before allowing booking
if student.semester_expiry and student.semester_expiry < datetime.utcnow().date():
    flash("Your semester has expired. Please renew.")
    return redirect(...)
```

**2. Approval Check**:
```python
if not student.is_approved:
    flash("Your account is pending approval.")
    return redirect(...)
```

**3. Seat Availability Check**:
```python
# Check if seat already booked
existing = Booking.query.filter_by(
    bus_id=bus_id,
    seat_number=seat_number,
    departure_time=departure_time,
    booking_date=today,
    direction=direction,
    status='Booked'
).first()

if existing:
    flash("Seat already booked.")
    return redirect(...)
```

**Should be Database Constraints** (recommended improvement):
```sql
-- Trigger to prevent booking if student not approved
CREATE TRIGGER check_student_approved
BEFORE INSERT ON bookings
FOR EACH ROW
WHEN (SELECT is_approved FROM students WHERE student_id = NEW.student_id) = 0
BEGIN
    SELECT RAISE(ABORT, 'Student not approved');
END;

-- Trigger to prevent booking if semester expired
CREATE TRIGGER check_semester_expiry
BEFORE INSERT ON bookings
FOR EACH ROW
WHEN (SELECT semester_expiry FROM students WHERE student_id = NEW.student_id) < DATE('now')
BEGIN
    SELECT RAISE(ABORT, 'Semester expired');
END;
```

---

## 10. Concurrency Control

### SQLite Locking Mechanism

**Lock Types**:
1. **UNLOCKED**: No locks
2. **SHARED**: Reading allowed, no writing
3. **RESERVED**: Preparing to write, others can still read
4. **PENDING**: Waiting for readers to finish
5. **EXCLUSIVE**: Writing, blocks all access

### Lock Escalation Example

**Scenario**: Two users booking simultaneously

**User A Timeline**:
```
T1: BEGIN TRANSACTION
    → Acquires SHARED lock (reading available seats)
T2: SELECT * FROM bookings WHERE ...
T3: INSERT INTO bookings ...
    → Attempts RESERVED lock
    → Escalates to EXCLUSIVE when ready to commit
T4: COMMIT
    → Releases all locks
```

**User B Timeline**:
```
T1: BEGIN TRANSACTION
    → Acquires SHARED lock
T2: SELECT * FROM bookings WHERE ...
T3: INSERT INTO bookings ...
    → Waits if User A has EXCLUSIVE lock
    → Proceeds after User A commits
T4: COMMIT or ROLLBACK (if conflict)
```

### Deadlock Prevention

**SQLite automatically prevents deadlocks**:
- Simple lock hierarchy
- Timeout mechanism (default 5 seconds)
- Automatic rollback on timeout

**Example**:
```python
try:
    booking = Booking(...)
    db.session.add(booking)
    db.session.commit()
except OperationalError as e:
    if 'database is locked' in str(e):
        db.session.rollback()
        # Retry logic or error message
```

---

### Transaction Isolation Levels

**SQLite Default**: **SERIALIZABLE**

**Comparison**:

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | SQLite Support |
|-----------------|------------|---------------------|--------------|----------------|
| READ UNCOMMITTED | Possible | Possible | Possible | No |
| READ COMMITTED | Not Possible | Possible | Possible | No |
| REPEATABLE READ | Not Possible | Not Possible | Possible | No |
| SERIALIZABLE | Not Possible | Not Possible | Not Possible | ✓ Default |

**Example: Phantom Read Prevention**

```python
# Transaction 1
bookings = Booking.query.filter_by(route_id=1).all()
count1 = len(bookings)
# Transaction 2 inserts new booking here
time.sleep(2)
bookings = Booking.query.filter_by(route_id=1).all()
count2 = len(bookings)
# count1 == count2 (SERIALIZABLE prevents phantom reads)
```

---

## 11. Advanced Database Concepts

### Triggers (Not Implemented - Possible Enhancement)

**Auto-update Student Status on Semester Expiry**:
```sql
CREATE TRIGGER update_expired_students
AFTER UPDATE ON students
FOR EACH ROW
WHEN NEW.semester_expiry < DATE('now') AND NEW.status != 'blocked'
BEGIN
    UPDATE students 
    SET status = 'pending'
    WHERE student_id = NEW.student_id;
END;
```

**Auto-cancel Bookings on Route Deactivation**:
```sql
CREATE TRIGGER cancel_bookings_inactive_route
AFTER UPDATE ON routes
FOR EACH ROW
WHEN NEW.status = 'inactive' AND OLD.status = 'active'
BEGIN
    UPDATE bookings
    SET status = 'Cancelled'
    WHERE route_id = NEW.route_id AND status = 'Booked';
END;
```

---

### Views (Recommended Enhancement)

**Active Bookings View**:
```sql
CREATE VIEW active_bookings AS
SELECT 
    b.booking_id,
    s.name AS student_name,
    s.email AS student_email,
    r.route_name,
    bu.bus_number,
    b.seat_number,
    b.departure_time,
    b.direction,
    b.booking_date
FROM bookings b
JOIN students s ON b.student_id = s.student_id
JOIN routes r ON b.route_id = r.route_id
JOIN buses bu ON b.bus_id = bu.bus_id
WHERE b.status = 'Booked' 
AND b.booking_date >= DATE('now')
AND s.is_approved = 1
AND s.status = 'active';
```

**Benefits**:
- Simplified queries
- Consistent business logic
- Easier reporting

---

### Stored Procedures (SQLite Alternative: User-Defined Functions)

**Python Implementation via SQLAlchemy**:

```python
from sqlalchemy import event

@event.listens_for(Student, 'before_insert')
def set_semester_expiry(mapper, connection, target):
    """Auto-set semester expiry to 6 months from approval"""
    if target.is_approved and not target.semester_expiry:
        target.semester_expiry = datetime.utcnow().date() + timedelta(days=180)

@event.listens_for(Booking, 'before_insert')
def validate_booking(mapper, connection, target):
    """Validate booking before insertion"""
    # Check student approval
    student = connection.execute(
        "SELECT is_approved FROM students WHERE student_id = ?",
        (target.student_id,)
    ).fetchone()
    
    if not student or not student[0]:
        raise ValueError("Student not approved for booking")
    
    # Check seat availability
    existing = connection.execute(
        """SELECT COUNT(*) FROM bookings 
           WHERE bus_id = ? AND seat_number = ? 
           AND departure_time = ? AND booking_date = ?
           AND direction = ? AND status = 'Booked'""",
        (target.bus_id, target.seat_number, target.departure_time,
         target.booking_date, target.direction)
    ).fetchone()
    
    if existing and existing[0] > 0:
        raise ValueError("Seat already booked")
```

---

## 12. Database Security

### SQL Injection Prevention

**Bad Practice** (vulnerable):
```python
# NEVER DO THIS
query = f"SELECT * FROM students WHERE email = '{email}'"
db.session.execute(query)
```

**Attack Example**:
```python
email = "admin@ex.com' OR '1'='1"
# Query becomes: SELECT * FROM students WHERE email = 'admin@ex.com' OR '1'='1'
# Returns all students!
```

**Good Practice** (SQLAlchemy):
```python
# Parameterized query
student = Student.query.filter_by(email=email).first()

# Or with raw SQL
student = db.session.execute(
    "SELECT * FROM students WHERE email = :email",
    {"email": email}
).fetchone()
```

---

### Password Hashing

**Implementation** (app.py):
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Registration
hashed = generate_password_hash(password, method='pbkdf2:sha256')
student = Student(password=hashed, ...)

# Login
if check_password_hash(student.password, password):
    # Authenticated
```

**Hash Storage**:
```
Input: "mypassword123"
Stored: "pbkdf2:sha256:260000$Xa2kF9$abc123def456..."
         └─── algorithm ──┘ └ iterations ┘ └─ salt ─┘ └─ hash ─┘
```

**Security Properties**:
- One-way function (irreversible)
- Unique salt per password
- Computationally expensive (prevents brute force)
- 260,000 iterations of SHA256

---

## 13. Performance Metrics

### Database Size Estimation

**Per Record Storage**:

```
Student: ~200 bytes
Admin: ~150 bytes
Route: ~300 bytes
Bus: ~150 bytes
Booking: ~100 bytes
Notice: ~500 bytes
```

**Example for 1000 students**:
```
Students: 1000 × 200 bytes = 200 KB
Bookings (avg 50/student): 50,000 × 100 bytes = 5 MB
Routes: 20 × 300 bytes = 6 KB
Buses (avg 5/route): 100 × 150 bytes = 15 KB
Notices: 100 × 500 bytes = 50 KB

Total ≈ 5.27 MB (without indexes)
With indexes: ~7.5 MB
```

---

### Query Performance Benchmarks

**Typical Query Times** (estimated on SQLite):

| Query | Without Index | With Index | Records |
|-------|--------------|------------|---------|
| Find student by email | 5-10ms | 1-2ms | 1000 |
| Get today's bookings | 20-30ms | 3-5ms | 10000 |
| Available seats | 15-25ms | 5-8ms | 1000 |
| Admin pending list | 10-15ms | 2-3ms | 1000 |

**Optimization Impact**:
- Indexes: 2-10x speedup
- Eager loading: Eliminates N+1 (10-100x for complex queries)
- Pagination: Constant time regardless of total records

---

## 14. Database Normalization Trade-offs Summary

### Current Design Decisions

| Decision | Normal Form | Trade-off | Justification |
|----------|-------------|-----------|---------------|
| JSON departure_times | Violates 1NF | Flexibility vs. Normalization | Simpler schema, acceptable for small datasets |
| Redundant route_id in Bookings | Denormalized | Storage vs. Query Speed | Faster filtering, explicit constraint |
| No separate table for Receipts | Potential 1NF issue | Simplicity vs. Extensibility | File path sufficient for MVP |

### Recommended Improvements

**1. Normalize Departure Times**:
```sql
CREATE TABLE departure_times (
    id INTEGER PRIMARY KEY,
    route_id INTEGER REFERENCES routes(route_id),
    time TIME NOT NULL,
    UNIQUE(route_id, time)
);
```

**2. Add Payment Receipts Table**:
```sql
CREATE TABLE payment_receipts (
    receipt_id INTEGER PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    file_path VARCHAR(255),
    upload_date DATETIME,
    verified BOOLEAN DEFAULT 0
);
```

**3. Add Indexes**:
```sql
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_student_date ON bookings(student_id, booking_date);
CREATE INDEX idx_students_status ON students(status);
```

---

## Conclusion

This DUTP database demonstrates:
- ✓ **Strong normalization** (BCNF for most tables)
- ✓ **Comprehensive constraints** (FK, CHECK, UNIQUE, NOT NULL)
- ✓ **ACID compliance** (Serializable transactions)
- ✓ **Referential integrity** (Cascade rules, FK enforcement)
- ✓ **Security** (Parameterized queries, password hashing)

**Areas for Enhancement**:
- Additional indexes for performance
- Normalize departure_times
- Implement database triggers
- Add materialized views
- Optimize with query caching
- Implement soft deletes (status-based instead of hard delete)

---

**Document Version**: 1.0  
**Last Updated**: December 4, 2025  
**Database Schema Version**: Current (DUTP MVP)
