import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re # For regular expressions to parse CPI Cutoff

# --- Configuration ---
# IMPORTANT: Corrected Login URL based on your previous error message
LOGIN_URL = "https://campus.placements.iitb.ac.in/auth/student/login" 
USERNAME = "" # Replace with your username
PASSWORD = "" # Replace with your password
BASE_JOB_URL = "https://campus.placements.iitb.ac.in/applicant/job/{}" # Base URL for individual JDs

# --- Your List of Job Codes ---
job_codes = [
    # Your full list of job codes goes here.
    '9936', '9946', '9218', '10106', '9729', '9728', '9134', '9368', '9035', '9428', '9038', '9018', '9027', '9020', '9022', '9024', '9025', '9026', '9034', '9036', '9037', '9039', '8942', '9061', '9380', '9388', '9389', '9390', '9411', '9412', '9420', '9425', '9426', '9456', '9711', '9569', '9567', '9568', '10075', '9496', '9277', '8997', '9369', '9695', '9371', '9370', '9479', '9220', '9208', '9207', '9206', '9797', '9937', '9939', '9482', '9731', '9732', '9653', '10086', '10085', '10084', '10083', '10082', '10081', '10080', '10079', '10078', '10071', '10059', '10382', '10297', '10294', '10293', '8961', '8962', '10250', '9473', '8965', '9888', '9491', '9525', '10209', '9145', '9714', '10335', '10336', '9211', '9127', '9212', '8880', '10227', '10226', '10222', '10221', '10219', '10217', '9438', '9896', '9515', '9513', '9512', '9489', '8924', '9563', '9562', '9577', '10122', '8816', '8812', '8811', '8813', '8815', '10159', '10162', '9160', '9158', '9157', '9176', '9174', '9171', '9268', '9102', '9275', '9642', '9944', '9580', '9559', '9775', '9418', '9970', '9122', '9915', '9210', '9108', '10133', '8862', '8861', '9373', '9136', '9107', '10304', '9397', '9699', '9485', '9486', '9700', '9487', '9698', '9488', '10100', '9619', '9213', '10029', '9455', '9104', '9752', '9980', '9153', '9155', '9152', '9151', '9150', '9149', '10036', '9641', '9374', '9776', '9130', '9131', '8936', '8935', '8932', '10002', '10143', '10142', '9918', '9119', '9121', '9901', '9490', '8938', '8939', '10289', '9897', '10047', '9457', '9542', '9543', '9180', '9178', '9179', '9177', '8944', '8945', '8946', '8947', '8948', '8949', '8950', '9000', '9003', '9006', '9050', '9054', '9156', '9161', '9183', '9053', '9055', '9835', '9836', '9837', '8982', '9926', '9927', '9929', '9928', '9639', '9638', '9230', '9092', '9410', '9900', '9602', '9603', '9604', '10030', '9267', '9911', '9909', '9910', '10249', '10273', '10240', '9640', '9253', '10330', '10331', '9112', '9117', '9118', '9682', '9976', '9175', '9791', '9270', '9271', '9594', '10134', '9734', '9733', '9692', '10033', '10314', '9244', '9950', '9943', '9898', '9059', '9925', '9687', '9219', '9376', '9058', '9852', '9867', '9816', '9201', '9665', '9792', '9793', '9841', '9741', '10327', '10001', '9214', '9088', '9807', '9076', '9075', '9074', '9073', '10311', '9942', '10118', '9096', '8978', '8977', '8975', '9955', '9818', '9770', '9111', '9126', '9678', '9981', '9982', '10279', '10280', '10281', '10282', '10177', '10186', '8993', '9592', '9590', '9591', '9586', '9585', '9582', '9008', '10375', '9702', '9056', '9993', '9988', '9989', '9990', '9460', '9461', '9462', '9463', '9465', '9466', '9467', '9468', '9469', '9471', '10389', '10390', '10379', '10380', '8790', '9833', '9527', '9167', '9168', '9264', '9265', '9072', '9071', '10127', '10043', '10042', '10040', '10039', '9742', '9876', '9875', '9023', '9877', '10363', '10361', '10038', '9202', '9949', '9497', '10278', '10268', '10091', '10011', '9593', '9596', '9595', '9042', '9552', '9553', '10027', '9234', '9235', '9236', '9239', '9238', '9237', '10116', '10115', '8941', '10046', '9040', '9605', '9861', '9521', '8929', '8976', '9647', '10145', '9996', '9997', '9693', '9684', '9685', '9691', '9760', '9761', '9780', '9781', '9782', '9783', '9784', '9069', '9932', '9899', '10008', '10019', '10021', '9464', '8796', '9560', '9574', '9614', '9814', '9887', '9774', '9172', '9892', '10105', '9953', '9956', '9246', '9759', '9769', '9772', '8960', '9987', '9021', '9879', '9880', '9878', '9617', '9070', '10296', '8979', '8998', '8985', '9085', '9245', '9066', '10006', '10004', '9484', '9481', '10077', '9798', '9623', '9019', '9045', '9827', '9828', '9830', '9044', '9043', '9041', '9191', '10114', '10074', '10073', '10072', '9399', '9400', '9401', '9402', '9403', '9404', '9204', '9133', '10052', '9408', '9478', '9840', '8895', '9139', '9386', '9857', '9858', '9902', '9916', '9964', '9966', '9967', '9968', '9249', '9248', '9263', '9885', '9806', '9146', '9147', '9148', '9398', '9259', '9256', '9391', '9170', '9372', '9123', '9124', '9514', '9432', '9433', '9379', '9523', '9894', '9890', '9868', '9869', '9870', '9812', '9415', '9261', '9260', '9262', '10135', '10137', '9532', '9278', '9526', '9848', '9566', '9884', '9435', '9436', '9437', '9668', '9667', '9666', '9387', '9703', '10332', '10117', '9474', '9476', '9655', '9475', '9838', '9493', '9166', '9164', '9163', '9165', '9162', '9115', '9113', '10045', '9862', '9502', '9674', '9637', '9704', '9615', '9622', '9628', '9652', '10276', '9796', '9832', '9933', '9983', '9984', '9985', '10090', '9722', '9846', '9708', '9712', '10253', '10259', '10260', '9715', '9749', '9883', '8923', '9743', '9860', '10007', '9804', '9903', '10267', '9809', '10215', '10216', '10214', '10213', '9863', '9920', '10263', '10264', '9881', '9906', '9907', '9908', '9923', '8984', '9009', '9010', '9062', '9063', '10284', '9948', '9922', '9921', '9931', '10290', '10016', '10211', '10358', '10310', '10309', '10308', '10307', '10012', '10013', '10014', '10015', '10305', '10088', '10054', '10032', '10355', '10034', '10035', '10124', '10126', '10110', '10104', '10299', '10136', '10274', '10093', '10107', '10108', '10109', '10312', '10328', '10329', '10202', '10204', '10119', '10121', '10125', '10141', '10140', '10139', '10138', '10146', '10149', '10208', '10151', '10201', '10207', '10295', '10288', '10315', '10352', '10353', '10356', '10373', '10365', '10369', '10381', '9060', '9817', '10238', '10237', '10236', '10235', '10234', '10231', '10230', '10229', '10228', '10225', '10224', '10223', '10041', '9492', '9494', '9280', '9534', '9958', '9960', '9959', '9961', '8994', '8992', '9882', '8991', '9721', '9720', '9719', '9718', '9717', '9716', '8995', '8989', '8988', '8971', '8970', '8969', '8968', '8967', '9986', '10132', '9132', '9089', '9951', '9886', '9225', '9226', '9227', '9367', '9272', '10144', '9423', '9856', '9767', '9766', '9765', '9764', '9763', '9762', '9101', '9522', '8937', '9392', '9393', '10010', '9565', '9572', '10018', '9758', '10271', '10270', '10269', '9745', '10360', '9738', '9737', '9746', '9431', '9443', '9430', '9429', '9169', '9663', '10176', '9091', '9090', '10028', '10175', '10210', '9095', '9620', '9740', '9182'
]

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