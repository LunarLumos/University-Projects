# 🌼 Daffodil University Transport Portal (DUTP)

**Tech Stack**:
- **Backend**: Flask (Python)
- **Database**: MySQL + SQLAlchemy ORM
- **Frontend**: HTML5, CSS3 (cute & responsive), Vanilla JavaScript (Fetch API)
- **Auth**: Session-based (no JWT)
- **Password**: `bcrypt` hashing

## 📁 Project Structure

```
dutp/
├── app.py                  # Main Flask app
 
# 🌼 Daffodil University Transport Portal (DUTP)

**Developer:** Aifee Aadil  
**University:** Daffodil International University  
**Teacher / Supervisor:** Mr. Md. Nasimul Kader

---

## 🌟 Project Overview

The Daffodil University Transport Portal (DUTP) is a focused transport booking web application built with Flask and SQLAlchemy. It supports DIU student registration (DIU-only email), admin approval workflows, bus and route management, and an audited booking system with cancellation and time-based guards.

Designed for campus operations, DUTP emphasizes clear admin workflows, simple deployment, and enforceable business rules (special-route restrictions, receipt-based verification).

---

## 🎯 Key Features

- **DIU-only Registration:** Students register using `@diu.edu.bd` emails; server-side validation enforces the rule.  
- **Admin Approval Workflow:** Admin reviews pending registrations (receipt IDs visible) and activates students.  
- **Booking System:** Students can book seats per route/time; the system assigns seats and enforces per-day and per-direction limits.  
- **Special-route Policy:** Some routes (e.g., Campus ⇄ Banani, Campus ⇄ Gulshan) are restricted to students who registered for them.  
- **Time-based Guards & Cancellation Rules:** Bookings must be made ≥1 hour before departure; cancellations blocked within 15 minutes of departure; bookings marked `Traveled` after departure.  
- **Printable Receipts & Today View:** Single-page receipt for printing and a default "Today" bookings view.

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask, SQLAlchemy (MySQL-compatible) |
| **Frontend** | HTML5, Jinja2 templates, CSS3, Vanilla JavaScript, Bootstrap |
| **Auth** | Flask-JWT-Extended (JWT cookies) |
| **Storage** | MySQL / MariaDB (recommended); dev runtime tries to create/alter missing schema for convenience |

---

## 🖌 UI & Design Highlights

- Responsive admin and student dashboards using Bootstrap.  
- Robust client-side interactions (data-attributes + centralized JS handlers).  
- Compact printable receipt layout optimized for one-page prints.

---

## 👨‍🏫 Teacher / Supervisor

**Mr. Md. Nasimul Kader** – Supervisor / Teacher  

---

## 👨‍💻 Developer

**Aifee Aadil** – Full-Stack Developer / Student  

---

## 🚀 Installation & Usage

1. **Clone the repository:**

```bash
git clone https://github.com/YourUsername/dutp.git
cd dutp
```

2. **Create & activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # zsh or bash
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure database & secrets:**
- Edit `config.py` or set environment variables, e.g.:

```bash
export DATABASE_URL='mysql+pymysql://user:pass@localhost/dutp'
export JWT_SECRET_KEY='change-me-in-prod'
export SECRET_KEY='change-me-in-prod'
```

5. **Run (development):**

```bash
python app.py
```

6. **Open:** http://127.0.0.1:5001

Notes
- Use Alembic in production for migrations; the app includes convenient runtime ALTERs for local development only.

---

## 📂 Project Structure

```
dutp/
├── app.py                  # Main Flask app (routes & glue)
├── models.py               # SQLAlchemy models (students, buses, routes, bookings)
├── config.py               # DB and secret configuration
├── requirements.txt        # Python dependencies
├── static/                 # CSS, JS, images
│   └── style.css
├── templates/              # Jinja2 templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── manage_students.html
│   └── my_bookings.html
└── README.md
```

---

## 📈 Future Enhancements

* Add Alembic migrations and a deploy checklist.  
* Create pytest coverage for core flows (registration, approval, booking rules).  
* Add secure image uploads for receipts and an admin image viewer.  
* Optional email notifications for key events.

---

## ❤️ Acknowledgements

* **Teacher:** Mr. Md. Nasimul Kader
* **University:** Daffodil International University
* **Developer:** Aifee Aadil

---

## � License

This project can be published under the **MIT License**. Add a `LICENSE` file when ready to publish.
- Expertise in Python, Flask, OOP, and frontend design  

- Created a fully functional, luxurious personal finance application  

