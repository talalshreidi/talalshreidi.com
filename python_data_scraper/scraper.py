from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time


def scrape_jobs(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for job listings to load 
        print("Waiting for jobs to load...")
        wait = WebDriverWait(driver, 30)
        
        # Wait until we have job rows that are not just placeholders
        wait.until(lambda driver: len([
            job for job in driver.find_elements(By.CSS_SELECTOR, "tr.job")
            if not job.get_attribute("class").find("placeholder") >= 0
        ]) > 0)
        
        # Give it a bit more time to fully load
        time.sleep(3)
        
        # Find all job elements 
        job_elements = [
            job for job in driver.find_elements(By.CSS_SELECTOR, "tr.job")
            if "placeholder" not in job.get_attribute("class")
        ]
        
        jobs = []
        print(f"Found {len(job_elements)} job postings.")
        
        for i, job in enumerate(job_elements):
            try:
                print(f"\n=== Job {i+1} ===")
                
                # Extract title
                try:
                    title_element = job.find_element(By.CSS_SELECTOR, "h2[itemprop='title']")
                    title_name = title_element.text.strip()
                except:
                    title_name = job.get_attribute("data-slug").replace("-", " ").title() if job.get_attribute("data-slug") else "Unknown Title"
                
                # Extract company
                try:
                    company_element = job.find_element(By.CSS_SELECTOR, "h3[itemprop='name']")
                    company_name = company_element.text.strip()
                except:
                    company_name = job.get_attribute("data-company") if job.get_attribute("data-company") else "Unknown Company"
                
                # Extract location
                try:
                    location_element = job.find_element(By.CSS_SELECTOR, "div.location")
                    location = location_element.text.strip()
                except:
                    location = "Remote"
                
                # Extract job link
                data_href = job.get_attribute("data-href")
                job_link = f"https://remoteok.com{data_href}" if data_href else ""
                
                # Extract tags
                tags = []
                try:
                    tag_elements = job.find_elements(By.CSS_SELECTOR, "div.tag h3")
                    tags = [tag.text.strip() for tag in tag_elements if tag.text.strip()]
                except:
                    pass
                
                # Extract time
                try:
                    time_element = job.find_element(By.CSS_SELECTOR, "time")
                    time_posted = time_element.get_attribute("datetime")
                except:
                    time_posted = "N/A"
                
                job_data = {
                    'title': title_name,
                    'company': company_name,
                    'location': location,
                    'link': job_link,
                    'tags': tags,
                    'time': time_posted
                }
                
                jobs.append(job_data)
                print(f"Successfully scraped: {title_name} at {company_name}")
                print(f"Location: {location}")
                print(f"Tags: {tags}")
                
            except Exception as e:
                print(f"Error parsing job {i+1}: {e}")
                continue
        
        driver.quit()
        return jobs
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()
        return []


if __name__ == "__main__":
    url = "https://remoteok.com/remote-python-jobs"
    jobs = scrape_jobs(url)
    print(f"\nTotal jobs scraped: {len(jobs)}")
    
    # Save to JSON file
    if jobs:
        with open('scraped_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print("Jobs saved to 'scraped_jobs.json'")