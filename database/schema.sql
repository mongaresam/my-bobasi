-- ============================================================
-- BOBASI NG-CDF BURSARY BORROWING SYSTEM - DATABASE SCHEMA
-- Bobasi Constituency, Kisii County, Kenya
-- 2025/2026 Financial Year
-- ============================================================
-- For MySQL/MariaDB production. SQLite is used in development
-- and auto-created by app.py via SQLAlchemy.
-- ============================================================

CREATE DATABASE IF NOT EXISTS bobasi_bursary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bobasi_bursary;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'finance_officer', 'review_committee') NOT NULL DEFAULT 'student',
    status ENUM('active', 'inactive', 'suspended') NOT NULL DEFAULT 'active',
    email_verified TINYINT(1) DEFAULT 0,
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- STUDENTS
-- ============================================================
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    admission_number VARCHAR(50) UNIQUE,
    institution VARCHAR(200),
    campus VARCHAR(200),
    course VARCHAR(200),
    year_of_study INT,
    level_of_study VARCHAR(50),
    date_of_birth VARCHAR(20),
    id_number VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    parent_phone VARCHAR(20),
    gender ENUM('male','female','other'),
    -- Location
    sub_county VARCHAR(100),
    division VARCHAR(100),
    location VARCHAR(100),
    sub_location VARCHAR(100),
    ward VARCHAR(100),
    polling_station VARCHAR(100),
    registered_voter VARCHAR(5),
    postal_address VARCHAR(200),
    -- Family
    family_status ENUM('total_orphan','partial_orphan','both_parents_alive') DEFAULT 'both_parents_alive',
    father_name VARCHAR(150),
    mother_name VARCHAR(150),
    guardian_name VARCHAR(150),
    guardian_phone VARCHAR(20),
    siblings_count INT DEFAULT 0,
    siblings_working INT DEFAULT 0,
    siblings_secondary INT DEFAULT 0,
    siblings_post_secondary INT DEFAULT 0,
    orphan_sponsor VARCHAR(200),
    another_sponsor VARCHAR(5),
    sponsor_details VARCHAR(200),
    prev_bursary VARCHAR(5),
    prev_bursary_years VARCHAR(100),
    prev_bursary_amount VARCHAR(50),
    -- Financial
    father_income DECIMAL(10,2) DEFAULT 0,
    mother_income DECIMAL(10,2) DEFAULT 0,
    self_income DECIMAL(10,2) DEFAULT 0,
    father_occupation VARCHAR(150),
    mother_occupation VARCHAR(150),
    household_income DECIMAL(10,2) DEFAULT 0,
    -- Bank & verification
    bank_ac_no VARCHAR(50),
    account_name VARCHAR(150),
    bank_branch VARCHAR(100),
    school_email VARCHAR(150),
    finance_person VARCHAR(150),
    finance_contact VARCHAR(20),
    principal_name VARCHAR(150),
    principal_contact VARCHAR(20),
    religious_leader VARCHAR(150),
    chief_name VARCHAR(150),
    profile_complete TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- APPLICATIONS
-- ============================================================
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    application_number VARCHAR(30) NOT NULL UNIQUE,
    academic_year VARCHAR(10) NOT NULL DEFAULT '2025/2026',
    semester ENUM('1','2','3') DEFAULT '1',
    institution VARCHAR(200),
    course VARCHAR(200),
    level_of_study VARCHAR(100),
    requested_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2) NULL,
    purpose TEXT,
    siblings_json TEXT,
    status ENUM('pending','under_review','approved','rejected','disbursed','completed') DEFAULT 'pending',
    rejection_reason TEXT NULL,
    committee_comments TEXT NULL,
    reviewed_by VARCHAR(100),
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME NULL,
    approved_at DATETIME NULL,
    disbursed_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ============================================================
-- DOCUMENTS
-- ============================================================
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    application_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_name VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100),
    status ENUM('pending','verified','rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- ============================================================
-- REVIEWS
-- ============================================================
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    decision ENUM('recommend_approval','recommend_rejection','need_more_info') NOT NULL,
    recommended_amount DECIMAL(10,2) NULL,
    comments TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- ============================================================
-- DISBURSEMENTS
-- ============================================================
CREATE TABLE disbursements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    student_id INT NOT NULL,
    finance_officer_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    disbursement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('bank_transfer','mpesa','cheque','cash') NOT NULL,
    bank_name VARCHAR(100) NULL,
    account_number VARCHAR(50) NULL,
    reference_number VARCHAR(100) UNIQUE,
    status ENUM('pending','processed','failed') DEFAULT 'processed',
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (finance_officer_id) REFERENCES users(id)
);

-- ============================================================
-- LOANS
-- ============================================================
CREATE TABLE loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    student_id INT NOT NULL,
    principal_amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) DEFAULT 0.00,
    repayment_period_months INT DEFAULT 24,
    monthly_installment DECIMAL(10,2),
    total_payable DECIMAL(10,2),
    balance_remaining DECIMAL(10,2),
    start_date VARCHAR(20),
    due_date VARCHAR(20),
    status ENUM('active','completed','defaulted','waived') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- ============================================================
-- REPAYMENTS
-- ============================================================
CREATE TABLE repayments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    student_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('bank_transfer','mpesa','cheque','cash') NOT NULL,
    reference_number VARCHAR(100),
    balance_remaining DECIMAL(10,2),
    recorded_by INT NULL,
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('application','disbursement','repayment','review','system') DEFAULT 'system',
    is_read TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_applications_student ON applications(student_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_loans_student ON loans(student_id);
CREATE INDEX idx_repayments_loan ON repayments(loan_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- ============================================================
-- SEED DATA - DEFAULT STAFF ACCOUNTS
-- Password for all: Admin@1234
-- Hash generated with Werkzeug generate_password_hash()
-- ============================================================
INSERT INTO users (name, email, password_hash, role, status, email_verified) VALUES
('System Administrator', 'admin@bobasi.go.ke',
 'pbkdf2:sha256:600000$bbs2025$a3e4f5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4',
 'admin', 'active', 1),
('Finance Officer', 'finance@bobasi.go.ke',
 'pbkdf2:sha256:600000$bbs2025$a3e4f5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4',
 'finance_officer', 'active', 1),
('Review Committee', 'review@bobasi.go.ke',
 'pbkdf2:sha256:600000$bbs2025$a3e4f5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4',
 'review_committee', 'active', 1);

-- NOTE: The password hashes above are placeholders.
-- Run `python app.py` to let the app auto-seed with correct bcrypt hashes.
-- OR use: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('Admin@1234'))"
-- to generate the correct hash and update the INSERT above.
