from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_sitemapper import Sitemapper
import bcrypt
import requests
import datetime
from dotenv import load_dotenv
import os

# Load environment variables before importing bard
load_dotenv()

# Now import bard so it can access PALM_API_KEY
import bard

# Load API keys from environment
api_key = os.environ.get("WEATHER_API_KEY")
secret_key = os.environ.get("SECRET_KEY", "fallback_super_secret_key")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secret_key

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

db = SQLAlchemy(app)

# Initialize sitemapper
sitemapper = Sitemapper(app=app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password.encode('utf8'))

# Create database tables
with app.app_context():
    db.create_all()

# Content Security Policy
@app.after_request
def add_csp_header(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://kit.fontawesome.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://emailjs.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://emailjs.com; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "manifest-src 'self'; "
        "media-src 'self'; "
        "worker-src 'self'; "
    )
    response.headers['Content-Security-Policy'] = csp
    return response

# Function to fetch weather data
def get_weather_data(api_key: str, location: str, start_date: str, end_date: str) -> dict:
    base_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}?unitGroup=metric&include=days&key={api_key}&contentType=json"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching weather:", e)
        return None

# Routes
@sitemapper.include()
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        source = request.form.get("source")
        destination = request.form.get("destination")
        start_date = request.form.get("date")
        end_date = request.form.get("return")

        no_of_day = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(start_date, "%Y-%m-%d")).days
        if no_of_day < 0:
            flash("Return date should be greater than the Travel date (Start date).", "danger")
            return redirect(url_for("index"))

        weather_data = get_weather_data(api_key, destination, start_date, end_date)
        if not weather_data:
            flash("Error in retrieving weather data.", "danger")
            return redirect(url_for("index"))

        plan = bard.generate_itinerary(source, destination, start_date, end_date, no_of_day)

        return render_template("dashboard.html", weather_data=weather_data, plan=plan)

    return render_template('index.html')

@sitemapper.include()
@app.route("/about")
def about():
    return render_template("about.html")

@sitemapper.include()
@app.route("/contact")
def contact():
    user_email = session.get('user_email', "Enter your email")
    user_name = session.get('user_name', "Enter your name")
    return render_template("contact.html", user_email=user_email, user_name=user_name, message='')

@sitemapper.include()
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash("Login successful.", "success")
            return redirect(url_for("index"))
        else:
            flash("Wrong email or password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@sitemapper.include()
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@sitemapper.include()
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        if password != password2:
            flash("Passwords do not match.", "danger")
            return redirect("/register")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists. Please log in.", "danger")
            return redirect("/login")

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect("/login")
    return render_template("register.html")

# Robots and Sitemap
@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')

@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Inject current time into templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# Run app
if __name__ == "__main__":
    #app.run(debug=True)
     import os
     port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default 5000
     app.run(host="0.0.0.0", port=port, debug=True)
