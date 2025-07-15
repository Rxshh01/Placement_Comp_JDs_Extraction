import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

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


   # <<< Replace with your password
LOGIN_URL = "https://campus.placements.iitb.ac.in/auth/student/login"
BASE_JOB_URL = "https://campus.placements.iitb.ac.in/applicant/job/{}"
INPUT_EXCEL = "data/Job_codes.csv"         # Excel with column 'job_code'
OUTPUT_CSV = "data/extracted_company_names.csv"  # Final output file

# === Helpers ===
def safe_text(soup, selector):
    tag = soup.select_one(selector)
    return tag.get_text(strip=True) if tag else "N/A"

def extract_job_details():
    # --- Load Excel job codes ---
    df_input = pd.read_csv(INPUT_EXCEL)
    job_codes = df_input["Job_Code"].astype(str).tolist()

    # --- Setup Selenium ---
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    all_data = []

    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)

        print("\n🔐 Waiting for manual login (solve CAPTCHA if needed)...")
        WebDriverWait(driver, 600).until(EC.url_changes(LOGIN_URL))
        print("✅ Login successful.")

        # --- Process Each Job ---
        for i, code in enumerate(job_codes):
            print(f"\n[{i+1}/{len(job_codes)}] Job Code: {code}")
            job_url = BASE_JOB_URL.format(code)

            try:
                driver.get(job_url)
                print(f"  Navigated to: {driver.current_url}")
                print(f"  Page title: {driver.title}")

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "p.panel-title.pt-4"))
                    )
                except:
                    print("  ⚠️ Warning: Key content may not be fully loaded")

                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # --- Extract Information ---
                company_name = safe_text(soup, "p.panel-title.pt-4")
                job_role = safe_text(soup, "h2.panel-title")
                job_type = safe_text(soup, ".job-designation")

                cpi_cutoff = "N/A"
                allow_bonus = "N/A"
                for h4 in soup.find_all("h4"):
                    text = h4.get_text(strip=True)
                    if "CPI Cutoff:" in text:
                        cpi_cutoff = text.split("CPI Cutoff:")[-1].strip()
                    elif "Allow bonus applications:" in text:
                        allow_bonus = text.split("Allow bonus applications:")[-1].strip()

# --- Extract Salary Info for B.Tech. ---
# --- Search all tables for the correct one ---
                salary_table = None
                for tbl in soup.find_all("table"):
                    if tbl.find("td") and "b.tech" in tbl.get_text().lower():
                        salary_table = tbl
                        break

                gross_salary = "N/A"
                ctc = "N/A"
                job_designation = "N/A"

                if salary_table:
                    rows = salary_table.find_all("tr")[1:]  # Skip header row
                    for row in rows:
                        cols = row.find_all("td")
                        if len(cols) >= 5:
                            program = cols[1].get_text(strip=True)
                            if "b.tech" in program.lower():
                                job_designation = cols[2].get_text(strip=True)
                                gross_salary = cols[3].get_text(strip=True).replace(",", "")
                                ctc = cols[4].get_text(strip=True).replace(",", "")
                                break
                else:
                    print("  ⚠️ Salary table with B.Tech. row not found.")


                # --- Append result ---
                all_data.append({
                    "Job Code": code,
                    "Company Name": company_name,
                    "Job Role": job_role,
                    "Job Type": job_type,
                    "CPI Cutoff": cpi_cutoff,
                    "Allow Bonus Applications": allow_bonus,
                    "B.Tech Job Designation": job_designation,
                    "B.Tech Gross Salary": gross_salary,
                    "B.Tech CTC": ctc
                })


            except Exception as e:
                print(f"❌ Error for job {code}: {e}")
                # Save debug info
                # with open(f"html_debug_{code}.html", "w", encoding="utf-8") as f:
                #     f.write(driver.page_source)
                # driver.save_screenshot(f"screenshot_{code}.png")

                all_data.append({
                    "Job Code": code,
                    "Company Name": "ERROR",
                    "Job Role": "ERROR",
                    "Job Type": "ERROR",
                    "CPI Cutoff": "ERROR",
                    "Allow Bonus Applications": "ERROR",
                    "B.Tech Gross Salary": "ERROR",
                    "B.Tech CTC": "ERROR",
                    "Error Details": str(e)
                })

            time.sleep(1)

    finally:
        driver.quit()

    # --- Save CSV ---
    df_out = pd.DataFrame(all_data)
    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ Data saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_job_details()
