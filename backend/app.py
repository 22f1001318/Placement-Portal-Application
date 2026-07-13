import csv
import os
import smtplib
import threading
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from flask import Flask, jsonify, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash


def create_app(testing=False, db_path=None):
    app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")
    app.config["SECRET_KEY"] = "placement-portal-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path or 'placement_portal.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing

    db = SQLAlchemy(app)
    cache_store = {}

    def get_cached(key, ttl_seconds, builder):
        now = time.time()
        cached_entry = cache_store.get(key)
        if cached_entry and (now - cached_entry["time"]) < ttl_seconds:
            return cached_entry["value"]

        value = builder()
        cache_store[key] = {"time": now, "value": value}
        return value

    def get_smtp_settings():
        return {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "22f1001318@ds.study.iitm.ac.in",
            "password": "Apple@123",
            "sender": "22f1001318@ds.study.iitm.ac.in",
        }

    def build_daily_reminder_message(upcoming_drives):
        if not upcoming_drives:
            return "Reminder: you have upcoming placement drives."

        names = ", ".join(drive.drive_name for drive in upcoming_drives[:3])
        return f"Reminder: upcoming drives - {names}"

    def build_monthly_report_html(number_of_drives, total_applications, completed_applications):
        return (
            "<h2>Placement Activity Report</h2>"
            f"<p>Drives conducted: {number_of_drives}</p>"
            f"<p>Applications: {total_applications}</p>"
            f"<p>Completed: {completed_applications}</p>"
        )

    def send_notification(recipient, message, subject="Placement Portal Notification", html_message=False):
        settings = get_smtp_settings()

        if not settings["host"] or not recipient or "@" not in recipient:
            return {"status": "queued", "recipient": recipient, "message": message}

        try:
            email_message = MIMEMultipart("alternative")
            email_message["Subject"] = subject
            email_message["From"] = settings["sender"]
            email_message["To"] = recipient
            email_message.attach(MIMEText(message, "html" if html_message else "plain"))

            if settings["port"] == 465:
                server = smtplib.SMTP_SSL(settings["host"], settings["port"], timeout=10)
            else:
                server = smtplib.SMTP(settings["host"], settings["port"], timeout=10)
                if os.getenv("SMTP_USE_TLS", "true").lower() != "false":
                    server.starttls()

            if settings["username"] and settings["password"]:
                server.login(settings["username"], settings["password"])

            server.sendmail(settings["sender"], [recipient], email_message.as_string())
            server.quit()
            return {"status": "sent", "via": "smtp", "recipient": recipient}
        except Exception as exc:
            return {"status": "failed", "error": str(exc)}

    def run_daily_reminders():
        results = []
        with app.app_context():
            upcoming_drives = PlacementDrive.query.filter(PlacementDrive.status != "Closed").all()
            students = User.query.filter_by(role="student").all()

            for student in students:
                if not student.email:
                    continue

                message = build_daily_reminder_message(upcoming_drives)
                status = send_notification(student.email, message, subject="Placement Reminder")
                results.append({"student_id": student.id, "email": student.email, **status})

        return results

    def run_monthly_report():
        with app.app_context():
            admin_user = User.query.filter_by(role="admin").first()
            number_of_drives = PlacementDrive.query.count()
            total_applications = Application.query.count()
            completed_applications = Application.query.filter_by(status="Completed").count()
            report_html = build_monthly_report_html(number_of_drives, total_applications, completed_applications)

            if admin_user:
                return send_notification(
                    admin_user.email or admin_user.username,
                    report_html,
                    subject="Monthly Placement Activity Report",
                    html_message=True,
                )

            return {"status": "skipped", "reason": "no admin"}

    def run_scheduled_tasks(now):
        if now.hour == 23 and now.minute == 35:
            run_daily_reminders()

        if now.day == 1 and now.hour == 0 and now.minute == 0:
            run_monthly_report()

    def start_background_jobs():
        def worker():
            while True:
                current_time = datetime.now()
                run_scheduled_tasks(current_time)
                time.sleep(60)

        threading.Thread(target=worker, daemon=True).start()

    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), nullable=False, default="student")
        user_type = db.Column(db.String(20), nullable=False, default="Student")
        display_name = db.Column(db.String(120), default="")
        department = db.Column(db.String(120), default="")
        email = db.Column(db.String(120), default="")
        is_active = db.Column(db.Boolean, default=True)

    class CompanyProfile(db.Model):
        __tablename__ = "company_profiles"
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
        company_name = db.Column(db.String(120), nullable=False)
        hr_contact = db.Column(db.String(120), nullable=False)
        website = db.Column(db.String(120), nullable=True)
        approval_status = db.Column(db.String(20), default="Pending")
        overview = db.Column(db.Text, default="")

    class PlacementDrive(db.Model):
        __tablename__ = "placement_drives"
        id = db.Column(db.Integer, primary_key=True)
        company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
        drive_name = db.Column(db.String(120), nullable=False)
        job_title = db.Column(db.String(120), nullable=False)
        job_description = db.Column(db.Text, nullable=False)
        eligibility = db.Column(db.String(200), nullable=False)
        application_deadline = db.Column(db.String(50), nullable=False)
        salary = db.Column(db.Integer, default=0)
        location = db.Column(db.String(120), default="")
        status = db.Column(db.String(20), default="Pending")

    class Application(db.Model):
        __tablename__ = "applications"
        id = db.Column(db.Integer, primary_key=True)
        student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
        drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
        application_date = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), default="Applied")
        remarks = db.Column(db.Text, default="")

    def ensure_schema():
        with app.app_context():
            db.create_all()
            inspector = inspect(db.engine)
            with db.engine.connect() as conn:
                if "users" in inspector.get_table_names():
                    user_columns = {column["name"] for column in inspector.get_columns("users")}
                    if "display_name" not in user_columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(120) DEFAULT ''"))
                    if "department" not in user_columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR(120) DEFAULT ''"))
                    if "email" not in user_columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120) DEFAULT ''"))
                if "company_profiles" in inspector.get_table_names():
                    company_columns = {column["name"] for column in inspector.get_columns("company_profiles")}
                    if "overview" not in company_columns:
                        conn.execute(text("ALTER TABLE company_profiles ADD COLUMN overview TEXT DEFAULT ''"))
                if "placement_drives" in inspector.get_table_names():
                    drive_columns = {column["name"] for column in inspector.get_columns("placement_drives")}
                    if "drive_name" not in drive_columns:
                        conn.execute(text("ALTER TABLE placement_drives ADD COLUMN drive_name VARCHAR(120) DEFAULT ''"))
                    if "salary" not in drive_columns:
                        conn.execute(text("ALTER TABLE placement_drives ADD COLUMN salary INTEGER DEFAULT 0"))
                    if "location" not in drive_columns:
                        conn.execute(text("ALTER TABLE placement_drives ADD COLUMN location VARCHAR(120) DEFAULT ''"))
                if "applications" in inspector.get_table_names():
                    application_columns = {column["name"] for column in inspector.get_columns("applications")}
                    if "remarks" not in application_columns:
                        conn.execute(text("ALTER TABLE applications ADD COLUMN remarks TEXT DEFAULT ''"))
                conn.commit()

    def initialize_app_state():
        with app.app_context():
            ensure_schema()
            start_background_jobs()
            if not User.query.filter_by(username="admin").first():
                admin = User(
                    username="admin",
                    password_hash=generate_password_hash("qwe123"),
                    role="admin",
                    user_type="Admin",
                    display_name="Admin",
                    is_active=True,
                )
                db.session.add(admin)
                db.session.commit()

    initialize_app_state()

    def current_user():
        user_id = session.get("user_id")
        if not user_id:
            return None
        return User.query.get(user_id)

    def company_profile_for_user(user):
        return CompanyProfile.query.filter_by(user_id=user.id).first()

    @app.route("/")
    def index():
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/src/<path:filename>")
    def serve_source(filename):
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        return send_from_directory(os.path.join(frontend_dir, "src"), filename)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/auth/register", methods=["POST"])
    def register():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        confirm_password = payload.get("confirm_password") or ""
        user_type = (payload.get("user_type") or "Student").strip()
        display_name = (payload.get("display_name") or payload.get("student_name") or payload.get("company_name") or "").strip()
        department = (payload.get("department") or "").strip()
        email = (payload.get("email") or "").strip()

        if not username or not password or password != confirm_password:
            return jsonify({"success": False, "message": "Please provide valid credentials"}), 400

        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({"success": False, "message": "Username already exists"}), 400

        role = "company" if user_type.lower() == "company" else "student"
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            user_type=user_type,
            display_name=display_name,
            department=department,
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()

        if role == "company":
            profile = CompanyProfile(
                user_id=new_user.id,
                company_name=display_name or username,
                hr_contact=payload.get("hr_contact", "N/A"),
                website=payload.get("website", ""),
                approval_status="Pending",
                overview="",
            )
            db.session.add(profile)
            db.session.commit()

        return jsonify({"success": True, "message": "Registration successful", "user_id": new_user.id})

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        payload = request.get_json(silent=True) or {}
        username_input = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        username = username_input
        if username.lower() == "sdmin":
            username = "admin"
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        if not user.is_active:
            return jsonify({"success": False, "message": "Account is disabled"}), 403
        if user.role == "company":
            profile = company_profile_for_user(user)
            if not profile or profile.approval_status != "Approved":
                return jsonify({"success": False, "message": "Please contact admin"}), 403
        session["user_id"] = user.id
        session["role"] = user.role
        return jsonify({"success": True, "message": "Logged in", "role": user.role, "user_type": user.user_type})

    @app.route("/api/logout", methods=["POST"])
    def logout():
        session.clear()
        return jsonify({"success": True, "message": "Logged out"})

    @app.route("/api/me")
    def me():
        user = current_user()
        if not user:
            return jsonify({"success": False, "message": "Not logged in"}), 401
        return jsonify({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "user_type": user.user_type,
            "display_name": user.display_name,
            "department": user.department,
            "email": user.email,
        })

    @app.route("/api/dashboard")
    def dashboard():
        user = current_user()
        if not user:
            return jsonify({"success": False, "message": "Not logged in"}), 401
        if user.role == "company":
            profile = company_profile_for_user(user)
            if not profile:
                return jsonify({"role": "company", "profile": {"company_name": "", "overview": ""}, "upcoming": [], "closed": []})

            company_drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
            upcoming_drives = [
                {"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title, "status": drive.status}
                for drive in company_drives
                if drive.status != "Closed"
            ]
            closed_drives = [
                {"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title, "status": drive.status}
                for drive in company_drives
                if drive.status == "Closed"
            ]

            return get_cached(
                f"company_dashboard:{user.id}",
                30,
                lambda: {
                    "role": "company",
                    "profile": {"company_name": profile.company_name, "overview": profile.overview},
                    "upcoming": upcoming_drives,
                    "closed": closed_drives,
                },
            )

        if user.role == "admin":
            return get_cached(
                "admin_dashboard",
                20,
                lambda: {
                    "role": "admin",
                    "pending_companies": [
                        {"id": item.id, "username": item.username, "company_name": profile.company_name}
                        for item in User.query.filter_by(role="company").all()
                        if (profile := company_profile_for_user(item)) and profile.approval_status == "Pending"
                    ],
                    "approved_companies": [
                        {"id": item.id, "company_name": profile.company_name, "active": item.is_active}
                        for item in User.query.filter_by(role="company").all()
                        if (profile := company_profile_for_user(item)) and profile.approval_status == "Approved"
                    ],
                    "students": [
                        {"id": item.id, "display_name": item.display_name or item.username, "department": item.department, "active": item.is_active}
                        for item in User.query.filter_by(role="student").all()
                    ],
                    "drives": [
                        {"id": item.id, "drive_name": item.drive_name, "job_title": item.job_title, "status": item.status}
                        for item in PlacementDrive.query.filter(PlacementDrive.status != "Closed").all()
                    ],
                    "applications": [
                        {
                            "id": app.id,
                            "student_name": student.display_name or student.username if student else "",
                            "drive_name": drive.drive_name if drive else "",
                            "company_name": company.company_name if company else "",
                            "date": app.application_date,
                            "status": app.status,
                        }
                        for app in Application.query.filter(Application.status != "Completed").all()
                        for drive in [PlacementDrive.query.get(app.drive_id)]
                        for student in [User.query.get(app.student_id)]
                        for company in [CompanyProfile.query.get(drive.company_id) if drive else None]
                    ],
                },
            )

        profile = current_user()
        approved_companies = []
        for company_user in User.query.filter_by(role="company").all():
            profile_data = company_profile_for_user(company_user)
            if profile_data and profile_data.approval_status == "Approved":
                approved_companies.append(
                    {"id": company_user.id, "company_name": profile_data.company_name, "overview": profile_data.overview}
                )

        # Only show drives relevant to the logged-in student:
        # - drives the student has applied to (and are not closed)
        active_drives = []
        student_applications = Application.query.filter_by(student_id=profile.id).all()
        for application in student_applications:
            drive = PlacementDrive.query.get(application.drive_id)
            if not drive:
                continue
            if drive.status == "Closed":
                continue
            company = CompanyProfile.query.get(drive.company_id)
            company_user = User.query.get(company.user_id) if company else None
            if not (company and company_user and company_user.is_active and company.approval_status == "Approved"):
                continue
            active_drives.append(
                {
                    "id": drive.id,
                    "drive_name": drive.drive_name,
                    "job_title": drive.job_title,
                    "company_name": company.company_name,
                    "company_id": company_user.id,
                    "application_status": application.status,
                }
            )

        student_applications = []
        for application in Application.query.filter_by(student_id=profile.id).all():
            drive = PlacementDrive.query.get(application.drive_id)
            company = CompanyProfile.query.get(drive.company_id) if drive else None
            student_applications.append(
                {
                    "id": application.id,
                    "drive_name": drive.drive_name if drive else "",
                    "company_name": company.company_name if company else "",
                    "status": application.status,
                    "remarks": application.remarks,
                }
            )

        return jsonify(
            {
                "role": "student",
                "profile": {"display_name": profile.display_name or profile.username, "department": profile.department},
                "companies": approved_companies,
                "drives": active_drives,
                "applications": student_applications,
            }
        )

    @app.route("/api/company/overview", methods=["GET", "POST"])
    def company_overview():
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        profile = company_profile_for_user(user)
        if not profile:
            return jsonify({"success": False, "message": "No profile found"}), 404
        if request.method == "GET":
            return jsonify({"overview": profile.overview})
        payload = request.get_json(silent=True) or {}
        profile.overview = payload.get("overview", "")
        db.session.commit()
        return jsonify({"success": True, "message": "Overview saved"})

    @app.route("/api/company/drives", methods=["POST"])
    def create_company_drive():
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        profile = company_profile_for_user(user)
        if not profile:
            return jsonify({"success": False, "message": "Create a company profile first"}), 400
        payload = request.get_json(silent=True) or {}
        drive = PlacementDrive(
            company_id=profile.id,
            drive_name=payload.get("drive_name", "New Drive"),
            job_title=payload.get("job_title", "New Role"),
            job_description=payload.get("job_description", "Opportunity available"),
            eligibility=payload.get("eligibility", "Any eligible student"),
            application_deadline=payload.get("application_deadline", "2026-08-31"),
            salary=int(payload.get("salary") or 0),
            location=payload.get("location", ""),
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()
        return jsonify({"success": True, "message": "Drive saved", "id": drive.id})

    @app.route("/api/company/drives/<int:drive_id>", methods=["GET", "PUT"])
    def company_drive_detail(drive_id):
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        if request.method == "GET":
            return jsonify({"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title, "job_description": drive.job_description, "eligibility": drive.eligibility, "application_deadline": drive.application_deadline, "salary": drive.salary, "location": drive.location, "status": drive.status})
        payload = request.get_json(silent=True) or {}
        drive.drive_name = payload.get("drive_name", drive.drive_name)
        drive.job_title = payload.get("job_title", drive.job_title)
        drive.job_description = payload.get("job_description", drive.job_description)
        drive.eligibility = payload.get("eligibility", drive.eligibility)
        drive.application_deadline = payload.get("application_deadline", drive.application_deadline)
        drive.salary = int(payload.get("salary", drive.salary or 0))
        drive.location = payload.get("location", drive.location)
        db.session.commit()
        return jsonify({"success": True, "message": "Drive updated"})

    @app.route("/api/company/drives/<int:drive_id>/complete", methods=["POST"])
    def complete_company_drive(drive_id):
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        drive.status = "Closed"
        for app in Application.query.filter_by(drive_id=drive.id).all():
            app.status = "Completed"
        db.session.commit()
        return jsonify({"success": True, "message": "Drive marked as complete"})

    @app.route("/api/company/drives/<int:drive_id>/applications")
    def company_drive_applications(drive_id):
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        result = []
        for app in Application.query.filter_by(drive_id=drive.id).all():
            student = User.query.get(app.student_id)
            result.append({"id": app.id, "student_name": student.display_name or student.username if student else "", "department": student.department if student else "", "status": app.status})
        return jsonify({"drive": {"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title}, "applications": result})

    @app.route("/api/company/applications/<int:application_id>", methods=["GET", "POST"])
    def company_application(application_id):
        user = current_user()
        if not user or user.role != "company":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        app = Application.query.get(application_id)
        if not app:
            return jsonify({"success": False, "message": "Application not found"}), 404
        student = User.query.get(app.student_id)
        drive = PlacementDrive.query.get(app.drive_id)
        if request.method == "GET":
            return jsonify({"id": app.id, "student_name": student.display_name or student.username if student else "", "department": student.department if student else "", "drive_name": drive.drive_name if drive else "", "job_title": drive.job_title if drive else "", "status": app.status, "remarks": app.remarks})
        payload = request.get_json(silent=True) or {}
        app.status = payload.get("status", app.status)
        app.remarks = payload.get("remarks", app.remarks)
        db.session.commit()
        return jsonify({"success": True, "message": "Application updated"})

    @app.route("/api/student/profile", methods=["GET", "POST"])
    def student_profile():
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        if request.method == "GET":
            return jsonify({"display_name": user.display_name or user.username, "department": user.department})
        payload = request.get_json(silent=True) or {}
        user.department = payload.get("department", user.department)
        user.display_name = payload.get("display_name", user.display_name)
        db.session.commit()
        return jsonify({"success": True, "message": "Profile updated"})

    @app.route("/api/student/history")
    def student_history():
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        items = []
        for app in Application.query.filter_by(student_id=user.id).all():
            drive = PlacementDrive.query.get(app.drive_id)
            company = CompanyProfile.query.get(drive.company_id) if drive else None
            items.append({"id": app.id, "drive_name": drive.drive_name if drive else "", "job_title": drive.job_title if drive else "", "company_name": company.company_name if company else "", "result": app.status, "remarks": app.remarks})
        return jsonify({"display_name": user.display_name or user.username, "department": user.department, "history": items})

    @app.route("/api/student/companies")
    def student_companies():
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        companies = []
        for entry in User.query.filter_by(role="company").all():
            profile = company_profile_for_user(entry)
            if profile and profile.approval_status == "Approved":
                companies.append({"id": entry.id, "company_name": profile.company_name, "overview": profile.overview})
        return jsonify(companies)

    @app.route("/api/student/company/<int:company_id>/drives")
    def student_company_drives(company_id):
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        company_user = User.query.get(company_id)
        profile = company_profile_for_user(company_user) if company_user else None
        if not profile:
            return jsonify({"success": False, "message": "Company not found"}), 404
        drives = []
        for drive in PlacementDrive.query.filter_by(company_id=profile.id).all():
            if drive.status == "Pending":
                drives.append({"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title})
        return jsonify({"company_name": profile.company_name, "overview": profile.overview, "drives": drives})

    @app.route("/api/student/drives/<int:drive_id>")
    def student_drive_detail(drive_id):
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        return jsonify({"id": drive.id, "drive_name": drive.drive_name, "job_title": drive.job_title, "job_description": drive.job_description, "salary": drive.salary, "location": drive.location})

    @app.route("/api/student/apply/<int:drive_id>", methods=["POST"])
    def student_apply(drive_id):
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        if drive.status == "Closed":
            return jsonify({"success": False, "message": "Drive is completed"}), 400
        existing = Application.query.filter_by(student_id=user.id, drive_id=drive.id).first()
        if existing:
            return jsonify({"success": False, "message": "You already applied"}), 400
        if not user.department:
            return jsonify({"success": False, "message": "Please update your profile department"}), 400
        app = Application(student_id=user.id, drive_id=drive.id, application_date=datetime.utcnow().strftime('%Y-%m-%d'), status='Applied')
        db.session.add(app)
        db.session.commit()
        return jsonify({"success": True, "message": "Application submitted"})

    @app.route("/api/admin/dashboard")
    def admin_dashboard():
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        pending_companies = []
        for item in User.query.filter_by(role="company").all():
            profile = company_profile_for_user(item)
            if profile and profile.approval_status == "Pending":
                pending_companies.append({"id": item.id, "username": item.username, "company_name": profile.company_name})
        approved_companies = []
        for item in User.query.filter_by(role="company").all():
            profile = company_profile_for_user(item)
            if profile and profile.approval_status == "Approved":
                approved_companies.append({"id": item.id, "company_name": profile.company_name, "active": item.is_active})
        students = [{"id": item.id, "display_name": item.display_name or item.username, "department": item.department, "active": item.is_active} for item in User.query.filter_by(role="student").all()]
        drives = [{"id": item.id, "drive_name": item.drive_name, "job_title": item.job_title, "status": item.status} for item in PlacementDrive.query.filter(PlacementDrive.status != "Closed").all()]
        applications = []
        for app in Application.query.filter(Application.status != "Completed").all():
            drive = PlacementDrive.query.get(app.drive_id)
            student = User.query.get(app.student_id)
            company = CompanyProfile.query.get(drive.company_id) if drive else None
            applications.append({"id": app.id, "student_name": student.display_name or student.username if student else "", "drive_name": drive.drive_name if drive else "", "company_name": company.company_name if company else "", "date": app.application_date, "status": app.status})
        return jsonify({"pending_companies": pending_companies, "approved_companies": approved_companies, "students": students, "drives": drives, "applications": applications})

    @app.route("/api/admin/search")
    def admin_search():
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        query = (request.args.get("q") or "").strip().lower()
        if not query:
            return admin_dashboard()
        filtered = []
        for item in User.query.filter_by(role="company").all():
            profile = company_profile_for_user(item)
            if profile and query in (item.username + " " + profile.company_name + " " + (item.email or "") + " " + (profile.overview or "")).lower():
                filtered.append({"id": item.id, "type": "company", "username": item.username, "company_name": profile.company_name, "active": item.is_active})
        for item in User.query.filter_by(role="student").all():
            if query in (item.username + " " + (item.display_name or "") + " " + (item.department or "") + " " + (item.email or "")).lower():
                filtered.append({"id": item.id, "type": "student", "display_name": item.display_name or item.username, "department": item.department, "active": item.is_active})
        for drive in PlacementDrive.query.all():
            company = CompanyProfile.query.get(drive.company_id)
            if query in (drive.drive_name + " " + drive.job_title + " " + (company.company_name if company else "") + " " + drive.location).lower():
                filtered.append({"id": drive.id, "type": "drive", "drive_name": drive.drive_name, "job_title": drive.job_title, "company_name": company.company_name if company else "", "location": drive.location, "status": drive.status})
        return jsonify({"results": filtered})

    @app.route("/api/admin/companies/<int:user_id>/approve", methods=["POST"])
    def approve_company(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        company_user = User.query.get(user_id)
        if not company_user:
            return jsonify({"success": False, "message": "Company not found"}), 404
        profile = company_profile_for_user(company_user)
        if profile:
            profile.approval_status = "Approved"
            db.session.commit()
        return jsonify({"success": True, "message": "Company approved"})

    @app.route("/api/admin/companies/<int:user_id>/block", methods=["POST"])
    def block_company(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        company_user = User.query.get(user_id)
        if not company_user:
            return jsonify({"success": False, "message": "Company not found"}), 404
        company_user.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Company blocked"})

    @app.route("/api/admin/companies/<int:user_id>/unblock", methods=["POST"])
    def unblock_company(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        company_user = User.query.get(user_id)
        if not company_user:
            return jsonify({"success": False, "message": "Company not found"}), 404
        company_user.is_active = True
        db.session.commit()
        return jsonify({"success": True, "message": "Company unblocked"})

    @app.route("/api/admin/students/<int:user_id>/block", methods=["POST"])
    def block_student(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        student_user = User.query.get(user_id)
        if not student_user:
            return jsonify({"success": False, "message": "Student not found"}), 404
        student_user.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Student blocked"})

    @app.route("/api/admin/students/<int:user_id>/unblock", methods=["POST"])
    def unblock_student(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        student_user = User.query.get(user_id)
        if not student_user:
            return jsonify({"success": False, "message": "Student not found"}), 404
        student_user.is_active = True
        db.session.commit()
        return jsonify({"success": True, "message": "Student unblocked"})

    @app.route("/api/admin/drives/<int:drive_id>/complete", methods=["POST"])
    def admin_complete_drive(drive_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        drive.status = "Closed"
        for app in Application.query.filter_by(drive_id=drive.id).all():
            app.status = "Completed"
        db.session.commit()
        return jsonify({"success": True, "message": "Drive completed"})

    @app.route("/api/admin/drives/<int:drive_id>")
    def admin_drive_detail(drive_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return jsonify({"success": False, "message": "Drive not found"}), 404
        return jsonify({
            "id": drive.id,
            "drive_name": drive.drive_name,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "eligibility": drive.eligibility,
            "application_deadline": drive.application_deadline,
            "status": drive.status,
        })

    @app.route("/api/student/export")
    def student_export_history():
        user = current_user()
        if not user or user.role != "student":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        export_dir = Path(app.root_path).parent / "exports"
        export_dir.mkdir(exist_ok=True)
        filename = f"student_{user.id}_applications.csv"
        target = export_dir / filename
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Student ID", "Company Name", "Drive Title", "Application Status", "Date"])
            for app in Application.query.filter_by(student_id=user.id).all():
                drive = PlacementDrive.query.get(app.drive_id)
                company = CompanyProfile.query.get(drive.company_id) if drive else None
                writer.writerow([user.id, company.company_name if company else "", drive.drive_name if drive else "", app.status, app.application_date])
        if user.email:
            send_notification(user.email, f"Your CSV export is ready. File: {filename}", subject="Placement Portal Export Ready")
        return jsonify({"success": True, "message": "Export ready", "file": filename})

    @app.route("/api/admin/debug/reminders", methods=["POST"])
    def debug_reminders():
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        results = run_daily_reminders()
        return jsonify({"success": True, "message": "Reminders processed", "count": len(results), "results": results})

    @app.route("/api/admin/applications/<int:application_id>")
    def admin_application_detail(application_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Not allowed"}), 403
        application = Application.query.get(application_id)
        if not application:
            return jsonify({"success": False, "message": "Application not found"}), 404
        student = User.query.get(application.student_id)
        drive = PlacementDrive.query.get(application.drive_id)
        company = CompanyProfile.query.get(drive.company_id) if drive else None
        return jsonify({
            "id": application.id,
            "student_name": student.display_name or student.username if student else "",
            "drive_name": drive.drive_name if drive else "",
            "company_name": company.company_name if company else "",
            "status": application.status,
            "date": application.application_date,
            "remarks": application.remarks,
        })

    return app


app = create_app()
