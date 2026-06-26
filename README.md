# 🎓 Bobasi NG-CDF Bursary Borrowing System (BBS)

**Bobasi Constituency, Kisii County, Kenya — 2025/2026 Financial Year**

A production-grade full-stack web application for managing Bobasi NG-CDF bursary applications, committee reviews, fund disbursements, loan tracking, and repayments.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Navigate to project folder
cd bobasi_bbs

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application (auto-creates SQLite DB + seeds default users)
python app.py

# 5. Open your browser
# Public site:  http://localhost:5000
# Admin portal: http://localhost:5000/admin/dashboard
```

---

## 🏗️ Project Structure

```
bobasi_bbs/
├── app.py                          # Flask application factory
├── config.py                       # Configuration (dev/prod)
├── requirements.txt                # Python dependencies
│
├── models/
│   └── models.py                   # SQLAlchemy ORM models + seed function
│
├── routes/
│   ├── auth.py                     # Login, Register, Logout, Change Password
│   ├── student.py                  # Student dashboard, profile, loans
│   ├── application.py              # Apply, view, track, upload documents
│   ├── admin.py                    # Admin dashboard, reviews, reports, users
│   ├── finance.py                  # Disbursements, loans, repayments
│   └── api.py                      # JSON API endpoints
│
├── templates/
│   ├── base.html                   # Public site base layout
│   ├── auth/                       # home, login, register, change_password
│   ├── student/                    # dashboard, profile, my_applications, loans, notifications
│   ├── application/                # apply, view, track, upload_docs
│   ├── admin/                      # base, dashboard, applications, view_application
│   │                                 students, view_student, reports, users
│   ├── finance/                    # base, dashboard, disburse, disbursements
│   │                                 loans, repayment, repayments
│   └── errors/                     # 404, 403, 500
│
├── static/
│   ├── css/
│   │   ├── style.css               # Public site styles
│   │   ├── form.css                # Multi-step profile form styles
│   │   └── admin.css               # Admin/finance portal styles
│   ├── js/
│   │   ├── main.js                 # Public JS
│   │   └── admin.js                # Admin JS
│   └── uploads/                    # Uploaded student documents
│
└── database/
    └── bobasi_bursary.db           # SQLite database (auto-created)
```

---

## 👥 User Roles & Default Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| **Admin** | admin@bobasi.go.ke | Admin@1234 | Full system access |
| **Finance Officer** | finance@bobasi.go.ke | Admin@1234 | Disburse funds, record repayments |
| **Review Committee** | review@bobasi.go.ke | Admin@1234 | View & review applications |
| **Student** | *(Register yourself)* | *(Your password)* | Apply, track, view loans |

> ⚠️ **Change default passwords immediately in production!**

---

## 🔄 Application Workflow

```
Student Registers
       ↓
Completes Profile (6-step form)
       ↓
Submits Bursary Application
       ↓
Committee Reviews → Recommends Approval/Rejection
       ↓
Admin Makes Final Decision (Approve/Reject)
       ↓
Finance Officer Disburses Funds (Bank/M-Pesa/Cheque)
       ↓
Loan Record Created → Repayment Tracking Begins
       ↓
Finance Records Repayments → Loan Marked Complete
```

---

## 📌 Key URLs

### Public
| URL | Description |
|-----|-------------|
| `/` | Homepage with eligibility info |
| `/register` | Student registration |
| `/login` | User login |
| `/application/track?ref=BOB2025xxxxx` | Public application tracker |

### Student Portal
| URL | Description |
|-----|-------------|
| `/student/dashboard` | Student dashboard |
| `/student/profile` | Edit profile (6 steps) |
| `/student/applications` | All my applications |
| `/student/loans` | Loan & repayment history |
| `/student/notifications` | System notifications |
| `/application/apply` | Submit new application |
| `/application/<id>` | View application detail |

### Admin Portal
| URL | Description |
|-----|-------------|
| `/admin/dashboard` | Admin dashboard + stats |
| `/admin/applications` | All applications (filterable) |
| `/admin/application/<id>` | View + make decision + review |
| `/admin/students` | All registered students |
| `/admin/reports` | Reports by status/sub-county/institution |
| `/admin/users` | Manage system users |

### Finance Portal
| URL | Description |
|-----|-------------|
| `/finance/dashboard` | Finance dashboard |
| `/finance/disburse` | Process disbursement |
| `/finance/disbursements` | All disbursement records |
| `/finance/loans` | All loans |
| `/finance/repayment` | Record repayment |
| `/finance/repayments` | All repayment records |

### API
| URL | Description |
|-----|-------------|
| `/api/stats` | Dashboard statistics (JSON) |
| `/api/me` | Current user info (JSON) |
| `/api/application/<id>/status` | Application status (JSON) |

---

## 🗄️ Database Models

| Table | Purpose |
|-------|---------|
| `users` | Authentication, roles, session management |
| `students` | Full student profiles, location, family, financial info |
| `applications` | Bursary applications with status tracking |
| `documents` | Uploaded supporting documents |
| `reviews` | Committee review records |
| `disbursements` | Fund disbursement records |
| `loans` | Loan tracking per approved application |
| `repayments` | Repayment transaction records |
| `notifications` | System notifications per user |

---

## 📋 Student Profile Fields

The 6-step profile form captures:

1. **Personal** — Full name, DOB, ID number, gender, mobile numbers
2. **Location** — Sub-county, division, ward, polling station, voter status
3. **Family** — Family status (orphan/partial/both parents), siblings data, sponsors, previous bursary
4. **Academic** — Admission no., institution, campus, course, level, year of study
5. **Financial** — Father/mother/self income, occupations
6. **Bank & Verify** — Bank account, finance officer, principal, religious leader, chief

---

## 🔒 Security Features

- ✅ Password hashing with Werkzeug (PBKDF2-SHA256)
- ✅ Role-Based Access Control (RBAC) — 4 distinct roles
- ✅ Flask-Login session management
- ✅ File upload validation (type + size, max 10MB)
- ✅ Secure filename sanitization (Werkzeug)
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Route decorators enforcing role access

---

## 🌐 Sub-Counties Supported

- Bobasi Central
- Bobasi Chache
- Bobasi North
- Bobasi South West
- Matibabu
- Nyacheki
- Boochi/Tendere
- Boochi West

---

## 🚀 Production Deployment

```bash
# Install production server
pip install gunicorn

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your-very-long-secret-key-here

# Optional: Use MySQL instead of SQLite
export DATABASE_URL=mysql+pymysql://user:password@localhost/bursary_db

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

**Recommended Nginx config:**
```nginx
server {
    listen 80;
    server_name bursary.bobasi.go.ke;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/bobasi_bbs/static/;
    }
}
```

---

## 📦 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10 + Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Auth | Flask-Login + Werkzeug |
| Database | SQLite (dev) / MySQL (prod) |
| Migrations | Flask-Migrate (Alembic) |
| Frontend | Jinja2 templates + Vanilla JS |
| Charts | Chart.js |
| Fonts | Playfair Display + DM Sans |
| Server | Gunicorn (production) |

---

## 📞 Bobasi NG-CDF Offices

| Office | Location |
|--------|----------|
| **Head Office** | Next to D.C.C's Office, Off Hospital Road – Nyamache |
| **Branch** | Itumbe |
| **Branch** | Nyacheki |

📮 **Postal Address:** P.O BOX 98-40203, Nyamache

---

*Bobasi NG-CDF Bursary Borrowing System — Empowering students from Bobasi Constituency, Kisii County, Kenya*
