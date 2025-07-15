import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# === Config ===
# === Configuration ===
def get_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' not in line:
                continue
            key, value = line.strip().split(':', 1)
            key = key.strip().upper()
            value = value.strip().strip('"').strip("'")  # remove quotes if any
            if key in ['USERNAME', 'PASSWORD']:
                credentials[key] = value
                print(f"Found {key} -> {value}")
    return credentials

creds = get_credentials('user.txt')
USERNAME = creds.get('USERNAME', 'NOT_FOUND')
PASSWORD = creds.get('PASSWORD', 'NOT_FOUND')


LOGIN_URL = "https://campus.placements.iitb.ac.in/auth/student/login"
BASE_JOB_URL = "https://campus.placements.iitb.ac.in/applicant/job/{}"
INPUT_CSV = "data/Job_codes.csv"
OUTPUT_CSV = "data/iitb_extracted_salaries.csv"

# === Helpers ===
def safe_text(soup, selector):
    tag = soup.select_one(selector)
    return tag.get_text(strip=True) if tag else "N/A"

def extract_job_details():
    df = pd.read_csv(INPUT_CSV)
    job_codes = df["Job_Code"].astype(str).tolist()

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    all_data = []

    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        print("🔐 Waiting for CAPTCHA/manual login...")
        WebDriverWait(driver, 600).until(EC.url_changes(LOGIN_URL))
        print("✅ Login successful.\n")

        for i, code in enumerate(job_codes):
            print(f"[{i+1}/{len(job_codes)}] Processing Job Code: {code}")
            url = BASE_JOB_URL.format(code)

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.panel-title.pt-4")))
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # --- Extract Company Name ---
                company_name = safe_text(soup, "p.panel-title.pt-4")

                # --- Extract Salary Info for B.Tech ---
                job_designation, gross_salary, ctc = "N/A", "N/A", "N/A"
                tables = soup.find_all("table")
                for table in tables:
                    rows = table.find_all("tr")[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all("td")
                        if len(cols) >= 5 and "b.tech" in cols[1].get_text(strip=True).lower():
                            job_designation = cols[2].get_text(strip=True)
                            gross_salary = cols[3].get_text(strip=True).replace(",", "")
                            ctc = cols[4].get_text(strip=True).replace(",", "")
                            break
                    if job_designation != "N/A":
                        break

                all_data.append({
                    "Job Code": code,
                    "Company Name": company_name,
                    "B.Tech Job Designation": job_designation,
                    "B.Tech Gross Salary": gross_salary,
                    "B.Tech CTC": ctc
                })

            except Exception as e:
                print(f"❌ Error for job {code}: {e}")
                all_data.append({
                    "Job Code": code,
                    "Company Name": "ERROR",
                    "B.Tech Job Designation": "ERROR",
                    "B.Tech Gross Salary": "ERROR",
                    "B.Tech CTC": "ERROR",
                    "Error Details": str(e)
                })

            time.sleep(1)

    finally:
        driver.quit()

    pd.DataFrame(all_data).to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ Results saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_job_details()
