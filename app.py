from flask import Flask, jsonify, render_template, request
from datetime import datetime
from projects import PROJECTS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from python_data_scraper import scraper
from python_data_scraper.blueprint import scraper_bp  
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-development-key")

app.register_blueprint(scraper_bp, url_prefix="/job-scraper-demo")

# Email configuration
PROTON_EMAIL = os.getenv("PROTON_EMAIL")  
PROTON_TOKEN = os.getenv("PROTON_TOKEN")  
SMTP_SERVER = "smtp.protonmail.ch"        
SMTP_PORT = 587                          

# CSRF protection
csrf = CSRFProtect(app)

# Create a proper form class
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])

@app.route("/")
def home():
    year = datetime.now().year
    return render_template("index.html", year=year)

@app.route("/skills")
def skills():
    return render_template("skills.html")

@app.route("/projects")
def projects():
    return render_template("projects.html", projects=PROJECTS)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    
    if request.method == 'POST':
        print(f"Form data received: {request.form}")
        print(f"Form validation: {form.validate_on_submit()}")
        print(f"Form errors: {form.errors}")
        
        if form.validate_on_submit():
            try:
                # Get form data
                name = form.name.data
                email = form.email.data 
                subject = form.subject.data
                message = form.message.data
                
                # Check if email configuration is available
                if not PROTON_EMAIL or not PROTON_TOKEN:
                    print("Email configuration missing!")
                    return jsonify({'success': False, 'message': 'Email service not configured'})
                
                msg = MIMEMultipart()
                msg['From'] = PROTON_EMAIL
                msg['To'] = PROTON_EMAIL
                msg['Subject'] = f"Portfolio Contact: {subject}"
                msg['Reply-To'] = email

                # Add anti-spam headers
                msg['X-Priority'] = '3'
                msg['X-MSMail-Priority'] = 'Normal'
                msg['X-Mailer'] = 'Portfolio Contact Form'
                msg['X-MimeOLE'] = 'Produced By Portfolio App'

                body = f"""
                PORTFOLIO CONTACT FORM SUBMISSION

                From: {name} <{email}>
                Subject: {subject}

                Message:
                {message}

                --
                This is an automated message from your portfolio website.
                To reply, respond directly to this email.
                Contact received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """

                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(PROTON_EMAIL, PROTON_TOKEN)
                    server.send_message(msg)
                
                print(f"Contact form email sent successfully from {name} ({email})")
                return jsonify({'success': True, 'message': 'Thank you for your message! I\'ll get back to you soon.'})
                
            except smtplib.SMTPAuthenticationError:
                print("SMTP Authentication failed - check email credentials")
                return jsonify({'success': False, 'message': 'Email authentication failed. Please try again later.'})
                
            except smtplib.SMTPException as e:
                print(f"SMTP error occurred: {e}")
                return jsonify({'success': False, 'message': 'Failed to send email. Please try again later.'})
                
            except Exception as e:
                print(f"Unexpected error: {e}")
                return jsonify({'success': False, 'message': 'An unexpected error occurred. Please try again later.'})
        else:
            # Form validation failed
            print("Form validation failed")
            return jsonify({'success': False, 'message': 'Please check your form inputs and try again.'})
    
    # GET request or form validation failed
    return render_template("contact.html", form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(rule)

# Add configuration class
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'fallback-development-key')
    DEBUG = False  # Default to False for production

class DevelopmentConfig(Config):
    DEBUG = True

# Apply config based on environment
if os.getenv('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(Config)

# Move logging setup here (outside of if __name__)
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/portfolio.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Portfolio application startup')

# Add after load_dotenv()
required_env_vars = ['FLASK_SECRET_KEY', 'PROTON_EMAIL', 'PROTON_TOKEN']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars and not app.debug:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

@app.after_request
def after_request(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)