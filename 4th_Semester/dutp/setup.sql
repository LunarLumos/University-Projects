USE dutp;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    semester_expiry DATE
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_name VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL,
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20)
);

CREATE TABLE routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    departure_point VARCHAR(100),
    destination_point VARCHAR(100),
    departure_time TIME,
    return_time TIME
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    bus_id INT,
    route_id INT,
    seat_number INT,
    status VARCHAR(20) DEFAULT 'Booked',
    booking_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
);

CREATE TABLE notices (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150),
    message TEXT,
    route_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    created_by VARCHAR(100),
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE SET NULL
);

-- 🔑 Admin: email=admin@daffodilvarsity.edu.bd, password=admin123
INSERT INTO admins (name, email, password)
VALUES ('Admin User', 'admin@daffodilvarsity.edu.bd', '$2b$12$vs.vLIPtr5YERD4cOw6BdO6zit23m48CJ5aJok7oiHs2d5rXfPWgK');

--  Sample Student: email=john@daffodilvarsity.edu.bd, password=student123
INSERT INTO students (name, email, password, is_approved, semester_expiry)
VALUES ('John Doe', 'john@daffodilvarsity.edu.bd', '$2b$12$1E5VOSI28C8pgy445sooHumJ2eQAuAnigT4aihfJ0fLB62tSEOXNy', TRUE, '2025-12-31');

--  Buses
INSERT INTO buses (bus_name, total_seats, driver_name, driver_phone)
VALUES 
(' DIU BUS 01', 40, 'Abdul Karim', '+8801712345678'),
(' DIU BUS 02', 35, 'Rahim Mia', '+8801812345678');

--  Routes
INSERT INTO routes (route_name, departure_point, destination_point, departure_time, return_time)
VALUES 
('Campus ⇄ Mirpur', 'DIU Main Campus', 'Mirpur 10', '07:30:00', '17:00:00'),
('Campus ⇄ Uttara', 'DIU Main Campus', 'Uttara Sector 4', '08:00:00', '17:30:00');

--  System notice
INSERT INTO notices (title, message, route_id, valid_until, created_by)
VALUES ('Welcome!', 'New semester registration is open!', NULL, DATE_ADD(NOW(), INTERVAL 30 DAY), 'System');
