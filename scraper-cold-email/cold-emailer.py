import requests
import time
import csv
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HVACLeadScraper:
    def __init__(self):
        self.companies = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def scrape_google_maps(self, query, location, max_results=50):
        """Scrape HVAC companies from Google Maps"""
        driver = self.setup_driver()
        companies = []
        
        try:
            search_url = f"https://www.google.com/maps/search/{query}+{location}"
            driver.get(search_url)
            time.sleep(5)
            
            # Scroll to load more results
            scrollable_div = driver.find_element(By.CSS_SELECTOR, "[role='main']")
            for i in range(10):  # Adjust scroll count as needed
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(2)
            
            # Extract business information
            business_elements = driver.find_elements(By.CSS_SELECTOR, "[data-result-index]")
            
            for element in business_elements[:max_results]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "[data-result-index] h3").text
                    
                    # Try to get rating and reviews
                    rating = "N/A"
                    reviews = "0"
                    try:
                        rating_element = element.find_element(By.CSS_SELECTOR, "[role='img'][aria-label*='stars']")
                        rating_text = rating_element.get_attribute('aria-label')
                        rating = re.search(r'(\d+\.?\d*)', rating_text).group(1) if rating_text else "N/A"
                        
                        reviews_element = element.find_element(By.CSS_SELECTOR, "[aria-label*='reviews']")
                        reviews_text = reviews_element.text
                        reviews = re.search(r'(\d+)', reviews_text).group(1) if reviews_text else "0"
                    except:
                        pass
                    
                    # Click to get more details
                    element.click()
                    time.sleep(3)
                    
                    # Extract additional details
                    phone = "N/A"
                    website = "N/A"
                    address = "N/A"
                    
                    try:
                        phone_elements = driver.find_elements(By.CSS_SELECTOR, "[data-item-id*='phone']")
                        if phone_elements:
                            phone = phone_elements[0].get_attribute('aria-label').replace('Phone: ', '')
                    except:
                        pass
                    
                    try:
                        website_elements = driver.find_elements(By.CSS_SELECTOR, "[data-item-id*='authority']")
                        if website_elements:
                            website = website_elements[0].get_attribute('href')
                    except:
                        pass
                    
                    try:
                        address_elements = driver.find_elements(By.CSS_SELECTOR, "[data-item-id*='address']")
                        if address_elements:
                            address = address_elements[0].get_attribute('aria-label').replace('Address: ', '')
                    except:
                        pass
                    
                    company_data = {
                        'name': name,
                        'phone': phone,
                        'website': website,
                        'address': address,
                        'rating': rating,
                        'reviews': reviews,
                        'source': 'Google Maps'
                    }
                    
                    companies.append(company_data)
                    logging.info(f"Scraped: {name}")
                    
                except Exception as e:
                    logging.error(f"Error scraping business: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error in Google Maps scraping: {e}")
        finally:
            driver.quit()
            
        return companies

    def scrape_yelp(self, location, max_results=50):
        """Scrape HVAC companies from Yelp"""
        companies = []
        
        for page in range(1, 6):  # First 5 pages
            try:
                url = f"https://www.yelp.com/search?find_desc=hvac&find_loc={location}&start={page*10}"
                response = self.session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                businesses = soup.find_all('div', {'data-testid': 'serp-ia-card'})
                
                for business in businesses:
                    try:
                        name_element = business.find('a', {'data-analytics-label': 'biz-name'})
                        name = name_element.text.strip() if name_element else "N/A"
                        
                        phone_element = business.find('div', {'data-testid': 'business-phone'})
                        phone = phone_element.text.strip() if phone_element else "N/A"
                        
                        address_element = business.find('p', {'data-testid': 'business-address'})
                        address = address_element.text.strip() if address_element else "N/A"
                        
                        rating_element = business.find('div', {'role': 'img'})
                        rating = rating_element.get('aria-label', 'N/A') if rating_element else "N/A"
                        
                        company_data = {
                            'name': name,
                            'phone': phone,
                            'website': "N/A",
                            'address': address,
                            'rating': rating,
                            'reviews': "N/A",
                            'source': 'Yelp'
                        }
                        
                        companies.append(company_data)
                        logging.info(f"Scraped from Yelp: {name}")
                        
                    except Exception as e:
                        logging.error(f"Error scraping Yelp business: {e}")
                        continue
                
                time.sleep(random.uniform(2, 4))  # Rate limiting
                
            except Exception as e:
                logging.error(f"Error scraping Yelp page {page}: {e}")
                continue
                
        return companies[:max_results]

    def find_email_from_website(self, website_url):
        """Extract email from company website"""
        if not website_url or website_url == "N/A":
            return "N/A"
            
        try:
            response = self.session.get(website_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common email patterns
            email_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
            ]
            
            text_content = soup.get_text()
            
            for pattern in email_patterns:
                emails = re.findall(pattern, text_content)
                if emails:
                    # Filter out common generic emails and return the first business email
                    for email in emails:
                        if not any(generic in email.lower() for generic in 
                                 ['noreply', 'donotreply', 'marketing', 'newsletter']):
                            return email
                            
        except Exception as e:
            logging.error(f"Error extracting email from {website_url}: {e}")
            
        return "N/A"

    def save_to_csv(self, companies, filename="hvac_leads.csv"):
        """Save companies to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'phone', 'website', 'email', 'address', 'rating', 'reviews', 'source']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for company in companies:
                writer.writerow(company)
                
        logging.info(f"Saved {len(companies)} companies to {filename}")

class EmailCampaign:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        
    def create_personalized_email(self, company_name, recipient_email):
        """Create personalized cold email"""
        
        # Multiple email templates for variety
        templates = [
            {
                'subject': f"Cut 3 Hours/Day from {company_name}'s Scheduling",
                'body': f"""Hi there,

I noticed {company_name} on Google Maps and saw you have great reviews - clearly you're doing quality work.

I'm reaching out because I've built something that's saving HVAC companies like yours 2-3 hours per day on scheduling alone.

Here's what it does:
• Auto-assigns the right technician based on location, skills, and availability
• Sends automatic appointment confirmations and reminders (cuts no-shows by 40%)
• Handles follow-up surveys that increase repeat business by 25-30%

The business owner I just delivered this to said: "This is like having a full-time scheduler, but it never calls in sick."

Would you be interested in a 10-minute demo showing how this works for HVAC companies specifically?

I can show you the exact ROI numbers and how it integrates with your current process.

Best regards,
[Your Name]

P.S. The scheduling algorithm alone typically pays for itself in the first month just from the time savings."""
            },
            {
                'subject': f"Quick Question About {company_name}'s Scheduling",
                'body': f"""Hi,

Quick question - how much time does someone at {company_name} spend each day coordinating schedules, calling customers, and handling appointment changes?

I'm asking because I just finished building a system that automates this entire process for HVAC companies, and the results have been impressive:

✓ One client went from 3 hours/day scheduling to 15 minutes
✓ Another reduced no-shows by 40% with automated reminders
✓ Follow-up surveys are bringing back 30% more repeat customers

The system handles:
- Smart technician assignment based on location + skills
- Automatic customer confirmations and reminders  
- Post-service follow-up that drives repeat business

Would it be worth 10 minutes to show you how this works specifically for HVAC businesses?

I can demonstrate the exact workflow and show you the ROI calculations.

Best,
[Your Name]"""
            },
            {
                'subject': f"Saw {company_name}'s Reviews - Impressive Work",
                'body': f"""Hi,

I was looking at HVAC companies in your area and {company_name}'s reviews really stood out - clearly you're doing excellent work.

That's actually why I'm reaching out. I've built a scheduling and follow-up system specifically for HVAC businesses, and companies with your level of quality work see the biggest impact.

Here's what it's doing for other HVAC companies:
• Cutting scheduling time from hours to minutes each day
• Automatically sending appointment reminders (40% fewer no-shows)
• Following up with customers to drive repeat business (+25-30% return rate)

The owner of [Local HVAC Company] told me last week: "This system is like having a dedicated scheduler who never makes mistakes."

Since you clearly care about customer service (your reviews prove it), I think you'd appreciate how this maintains that quality while saving you significant time.

Would you be open to a brief demo showing exactly how it works for HVAC businesses?

Best regards,
[Your Name]

P.S. Happy to show you the specific ROI numbers and how it integrates with your current workflow."""
            }
        ]
        
        template = random.choice(templates)
        
        return template['subject'], template['body']

    def send_email(self, recipient_email, subject, body):
        """Send individual email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, recipient_email, text)
            server.quit()
            
            logging.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending email to {recipient_email}: {e}")
            return False

    def send_campaign(self, companies, delay_min=5, delay_max=15):
        """Send email campaign to all companies"""
        sent_count = 0
        
        for company in companies:
            if company.get('email') and company['email'] != "N/A":
                subject, body = self.create_personalized_email(
                    company['name'], 
                    company['email']
                )
                
                if self.send_email(company['email'], subject, body):
                    sent_count += 1
                    
                # Random delay between emails to avoid spam detection
                delay = random.uniform(delay_min, delay_max)
                time.sleep(delay)
                
        logging.info(f"Campaign completed. Sent {sent_count} emails.")

def main():
    # Configuration
    LOCATIONS = [
        "New York NY",
        "Los Angeles CA", 
        "Chicago IL",
        "Houston TX",
        "Phoenix AZ",
        # Add more cities as needed
    ]
    
    # Email configuration (use Gmail or other SMTP)
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email': 'your_email@gmail.com',  # Replace with your email
        'password': 'your_app_password'    # Use App Password for Gmail
    }
    
    # Initialize scraper
    scraper = HVACLeadScraper()
    all_companies = []
    
    # Scrape companies from multiple sources and locations
    for location in LOCATIONS:
        logging.info(f"Scraping HVAC companies in {location}")
        
        # Google Maps scraping
        google_companies = scraper.scrape_google_maps("HVAC contractor", location, max_results=30)
        all_companies.extend(google_companies)
        
        # Yelp scraping
        yelp_companies = scraper.scrape_yelp(location, max_results=20)
        all_companies.extend(yelp_companies)
        
        time.sleep(10)  # Rate limiting between locations
    
    # Remove duplicates
    unique_companies = []
    seen_names = set()
    
    for company in all_companies:
        if company['name'] not in seen_names:
            unique_companies.append(company)
            seen_names.add(company['name'])
    
    logging.info(f"Found {len(unique_companies)} unique companies")
    
    # Extract emails from websites
    for company in unique_companies:
        if company.get('website') and company['website'] != "N/A":
            email = scraper.find_email_from_website(company['website'])
            company['email'] = email
            time.sleep(2)  # Rate limiting
        else:
            company['email'] = "N/A"
    
    # Save to CSV
    scraper.save_to_csv(unique_companies)
    
    # Filter companies with emails for campaign
    companies_with_emails = [c for c in unique_companies if c.get('email') and c['email'] != "N/A"]
    logging.info(f"Found {len(companies_with_emails)} companies with email addresses")
    
    # Send email campaign
    if companies_with_emails:
        campaign = EmailCampaign(**EMAIL_CONFIG)
        
        # Send to first 10 companies as a test
        test_companies = companies_with_emails[:10]
        campaign.send_campaign(test_companies)
        
        print(f"Test campaign sent to {len(test_companies)} companies")
        print("Check your results and adjust before sending to the full list")

if __name__ == "__main__":
    main()