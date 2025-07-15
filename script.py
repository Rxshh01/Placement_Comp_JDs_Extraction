import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re # For regular expressions to parse CPI Cutoff
import ast
import re

with open("yourfile.txt", "r") as f:
    content = f.read()

# Regex to find something like: codes = [ ... ]
match = re.search(r'job_codes\s*=\s*(\[[^\]]*\])', content)
if match:
    job_codes = ast.literal_eval(match.group(1))

else:
    print("No codes list found.")

# --- Configuration ---
# IMPORTANT: Corrected Login URL based on your previous error message
LOGIN_URL = "https://campus.placements.iitb.ac.in/auth/student/login" 
USERNAME = "" # Replace with your username
PASSWORD = "" # Replace with your password
BASE_JOB_URL = "https://campus.placements.iitb.ac.in/applicant/job/{}" # Base URL for individual JDs

# --- Your List of Job Codes ---

# Output settings
OUTPUT_DIR = "fetched_jds" # Directory to save individual JD text files
OUTPUT_CSV_FILE = "raw_jds_summary.csv" # CSV file to summarize JDs and their raw text

# --- Main Script ---
def fetch_raw_jds_by_codes():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # Initialize WebDriver (for manual login with reCAPTCHA)
    options_for_manual_login = webdriver.ChromeOptions()
    # DO NOT add --headless here if you need to manually solve reCAPTCHA
    driver = webdriver.Chrome(options=options_for_manual_login) 

    all_jds_summary_data = [] # To store data for CSV export

    try:
        print(f"Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)

        # --- Login ---
        print("Waiting for login elements...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(USERNAME)

        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        # --- IMPORTANT: reCAPTCHA Handling (Requires Manual Intervention) ---
        print("\n--- ATTENTION: reCAPTCHA DETECTED ---")
        print("The 'Sign In' button is initially disabled due to reCAPTCHA.")
        print("You *MUST* manually solve the reCAPTCHA in the opened browser window.")
        print("After solving the reCAPTCHA, please click the 'Sign In' button manually.")
        print("The script will wait for the URL to change, indicating successful login.")

        # The script will now pause indefinitely until the URL changes (indicating manual login)
        print("\nWaiting for manual login (solve reCAPTCHA and click 'Sign In')...")
        WebDriverWait(driver, 1200).until( # Increased timeout to 20 minutes for manual intervention
            EC.url_changes(LOGIN_URL)
        )
        print("Logged in successfully (URL changed). Resuming script.")
        time.sleep(2) # Small pause after login for good measure


        # --- Iterate through provided Job Codes ---
        print(f"Starting to fetch {len(job_codes)} JDs...")
        for i, code in enumerate(job_codes):
            jd_link = BASE_JOB_URL.format(code)
            print(f"\nProcessing JD {i+1}/{len(job_codes)} (Code: {code}): {jd_link}")
            
            try:
                driver.get(jd_link)
                time.sleep(3) # Wait for JD page to load (adjust as needed)

                # Get the full page source after dynamic content loads
                jd_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # --- EXTRACT RAW JD TEXT ---
                # Based on your new info: class="panel mt-3 mb-3 d-flex flex-column"
                jd_content_div = jd_soup.find('div', class_='panel mt-3 mb-3 d-flex flex-column') 
                
                # Default values in case elements are not found
                company_name = "N/A"
                role_name = "N/A"
                raw_jd_text = ""
                cpi_cutoff = "N/A"
                ctc_btech = "N/A" # New field
                gross_salary_btech = "N/A" # New field

                # Try to extract company name and role name (keep previous selectors as a starting point, adjust if needed)
                company_name_element = jd_soup.find('h1', class_='company-name') 
                role_name_element = jd_soup.find('h2', class_='job-title') 

                company_name = company_name_element.get_text(strip=True) if company_name_element else "N/A"
                role_name = role_name_element.get_text(strip=True) if role_name_element else "N/A"

                if jd_content_div:
                    raw_jd_text = jd_content_div.get_text(separator='\n', strip=True)
                    print(f"  Company: {company_name}")
                    print(f"  Role: {role_name}")
                    print("  Raw JD text extracted successfully (first 200 chars):")
                    print(raw_jd_text[:200] + "...")
                else:
                    print(f"  Could not find main JD content div with class 'panel mt-3 mb-3 d-flex flex-column' for {jd_link}. Skipping raw JD text.")

                # --- EXTRACT CPI CUTOFF ---
                # Look for a div with class "mt-3" containing an h4 with "CPI Cutoff:"
                cpi_cutoff_div = jd_soup.find('div', class_='mt-3')
                if cpi_cutoff_div:
                    cpi_h4 = cpi_cutoff_div.find('h4', string=re.compile(r'CPI Cutoff:'))
                    if cpi_h4:
                        # Extract text after "CPI Cutoff:"
                        cpi_text = cpi_h4.get_text(strip=True)
                        match = re.search(r'CPI Cutoff:\s*(.*)', cpi_text)
                        if match:
                            cpi_cutoff = match.group(1).strip()
                            print(f"  CPI Cutoff: {cpi_cutoff}")
                        else:
                            print("CPI Cutoff text found, but could not parse value.")
                    else:
                        print("'CPI Cutoff:' h4 tag not found within the expected div.")
                else:
                    print("CPI Cutoff parent div (class='mt-3') not found.")


                # --- EXTRACT CTC and GROSS SALARY for B.Tech ---
                # This is the trickiest part as "ng-star-inserted" is very generic.
                # You need to carefully inspect the HTML around the CTC/Gross Salary.
                # Look for the specific table, row, or div that *uniquely* contains this information.
                # Below is a general approach. You might need to refine the selector (e.g., use a more specific class, a data attribute, or XPath).
                
                # Example strategy: Find all div elements with the generic class, then search their text.
                # This is prone to false positives if the structure isn't consistent.
                
                # A better approach usually involves looking for a parent table/div with a more unique identifier.
                # For example, if there's a table for "Compensation Details" you'd find that first.
                
                # Let's try to find elements that contain "CTC", "Gross Salary" and "B.Tech"
                
                # You'll likely need to customize this part HEAVILY based on exact HTML
                # Look for a common parent of these elements, e.g., a table or a specific div for salary details.
                # For demonstration, let's search for "B.Tech" within elements that also contain salary keywords.

                salary_info_container = jd_soup.find('div', class_='ng-star-inserted') # This is still too generic.
                                                                                       # You NEED to find a more specific parent for the salary info.
                                                                                       # E.g., if salaries are in a specific table:
                                                                                       # salary_table = jd_soup.find('table', class_='salary-details-table')
                                                                                       # Then search within that table.

                # Placeholder logic - this will likely need significant customization from you
                # based on the actual HTML structure of the salary section.
                # Iterate through all elements with 'ng-star-inserted' and check their text
                all_ng_star_inserted_elements = jd_soup.find_all(class_='ng-star-inserted')
                
                for elem in all_ng_star_inserted_elements:
                    text = elem.get_text(separator=' ', strip=True)
                    if "B.Tech" in text and ("CTC" in text or "Gross Salary" in text):
                        print(f"  Potential B.Tech Salary Info Found: {text[:100]}...") # Print a snippet
                        # You'll need to parse this 'text' to get CTC and Gross Salary.
                        # This requires knowing the exact format, e.g., "CTC: X, Gross: Y"
                        
                        # Example parsing (highly dependent on exact string format):
                        ctc_match = re.search(r'CTC:\s*([\d\.,]+)', text, re.IGNORECASE)
                        gross_match = re.search(r'Gross Salary:\s*([\d\.,]+)', text, re.IGNORECASE)
                        
                        if ctc_match:
                            ctc_btech = ctc_match.group(1).replace(',', '') # Remove commas
                        if gross_match:
                            gross_salary_btech = gross_match.group(1).replace(',', '')
                            
                        # If you find it, you might want to break or continue based on if there are multiple such rows
                        # For now, let's just take the first one found.
                        break # Assume we found the relevant one.

                if ctc_btech != "N/A" or gross_salary_btech != "N/A":
                    print(f"  CTC (B.Tech): {ctc_btech}, Gross Salary (B.Tech): {gross_salary_btech}")
                else:
                    print("  CTC/Gross Salary for B.Tech not specifically found in generic ng-star-inserted elements.")
                    print("  *** You NEED to manually inspect the HTML for the CTC/Gross Salary section for B.Tech ***")
                    print("  *** to create more precise selectors. 'ng-star-inserted' is usually too broad. ***")


                # --- Save and Summarize Data ---
                # Save raw JD to a text file
                clean_company_name = "".join([c for c in company_name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
                clean_role_name = "".join([c for c in role_name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
                file_name = f"{clean_company_name}_{clean_role_name}_{code}.txt"
                file_path = os.path.join(OUTPUT_DIR, file_name)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(raw_jd_text)
                print(f"  Saved raw JD to: {file_path}")

                # Add to summary data for CSV
                all_jds_summary_data.append({
                    "Company": company_name,
                    "Role": role_name,
                    "Job_Code": code,
                    "JD_Link": jd_link,
                    "Raw_JD_Text_File": file_path,
                    "Raw_JD_Text_Snippet": raw_jd_text[:500], # Store snippet for quick CSV view
                    "CPI_Cutoff": cpi_cutoff, # New field
                    "CTC_BTech": ctc_btech,    # New field
                    "Gross_Salary_BTech": gross_salary_btech # New field
                })

            except Exception as e:
                print(f"  Error processing {jd_link}: {e}")
                all_jds_summary_data.append({
                    "Company": "ERROR",
                    "Role": "ERROR",
                    "Job_Code": code,
                    "JD_Link": jd_link,
                    "Raw_JD_Text_File": "ERROR",
                    "Raw_JD_Text_Snippet": f"Error: {e}",
                    "CPI_Cutoff": "ERROR",
                    "CTC_BTech": "ERROR",
                    "Gross_Salary_BTech": "ERROR"
                })

    except Exception as e:
        print(f"\nAn error occurred during the main scraping process: {e}")
    finally:
        driver.quit() # Always close the browser when done

    # --- Create DataFrame and Export to CSV ---
    if all_jds_summary_data:
        df = pd.DataFrame(all_jds_summary_data)
        df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
        print(f"\nSuccessfully created '{OUTPUT_CSV_FILE}' with {len(all_jds_summary_data)} entries.")
    else:
        print("\nNo job data was extracted to write to CSV.")

# Run the script
if __name__ == "__main__":
    fetch_raw_jds_by_codes()