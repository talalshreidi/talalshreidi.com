import os
from flask import Blueprint, render_template, redirect, url_for, flash
from .scraper import scrape_jobs
from .db import init_db, save_jobs, get_all_jobs, clear_jobs, is_db_initialized
import datetime

# Define the blueprint
scraper_bp = Blueprint(
    "python_scraper",  # Blueprint name
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),  # Absolute path to templates
    static_folder=os.path.join(os.path.dirname(__file__), "static"),  # Absolute path to static files
)

# Inject current year into templates
@scraper_bp.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

# Initialize database only if it hasn't been initialized
@scraper_bp.before_app_request
def setup_database():
    if not is_db_initialized():
        init_db()

# Define the index route for the scraper
@scraper_bp.route("/")
def index():
    # Get all jobs from the database
    jobs = get_all_jobs()
    print(f"Displaying {len(jobs)} jobs on the scraper homepage")
    return render_template("python_scraper/index.html", jobs=jobs)

# Define the refresh route for the scraper
@scraper_bp.route("/refresh")
def refresh_jobs():
    try:
        print("=" * 50)
        print("Starting job refresh process...")

        # Clear old jobs from the database
        clear_jobs()

        # Scrape new jobs
        url = "https://remoteok.com/remote-python-jobs"
        scraped_jobs = scrape_jobs(url)
        print(f"Scraper returned {len(scraped_jobs)} jobs")

        if scraped_jobs:
            # Save new jobs to the database
            saved_count = save_jobs(scraped_jobs)
            if saved_count > 0:
                flash(f'🎉 Successfully refreshed! Found and saved {saved_count} new Python jobs.', 'success')
            else:
                flash('❌ Jobs were found but could not be saved to the database.', 'danger')
        else:
            flash('⚠️ No jobs found during scraping. The site might be down or changed.', 'warning')

        print("=" * 50)

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error during scraping: {str(e)}', 'danger')

    return redirect(url_for("python_scraper.index"))  # Use the blueprint name for the route