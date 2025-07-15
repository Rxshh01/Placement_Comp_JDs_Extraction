import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service # Still needed for Service object, but not ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re # For regular expressions to parse CPI Cutoff
import os # Needed for os.path.exists and os.makedirs if you were saving files, keeping it for now

# --- Configuration ---
# IMPORTANT: Replace with your actual username and password
USERNAME = "210040058" # Replace with your username
PASSWORD = "Harshit@1234" # <--- REPLACE WITH YOUR PASSWORD

LOGIN_URL = "https://campus.placements.iitb.ac.in/auth/student/login" 
BASE_JOB_URL = "https://campus.placements.iitb.ac.in/applicant/job/{}" # Base URL for individual JDs

# Your provided list of job codes (using a smaller list for quicker testing)
job_codes = [
    '9936', '9946', '9218', '10106', '9729', '9728', '9134', '9368', '9035', '9428' # Reduced for testing
    # Use your full list here for production:
    # '9936', '9946', '9218', '10106', '9729', '9728', '9134', '9368', '9035', '9428', '9038', '9018', '9027', '9020', '9022', '9024', '9025', '9026', '9034', '9036', '9037', '9039', '8942', '9061', '9380', '9388', '9389', '9390', '9411', '9412', '9420', '9425', '9426', '9456', '9711', '9569', '9567', '9568', '10075', '9496', '9277', '8997', '9369', '9695', '9371', '9370', '9479', '9220', '9208', '9207', '9206', '9797', '9937', '9939', '9482', '9731', '9732', '9653', '10086', '10085', '10084', '10083', '10082', '10081', '10080', '10079', '10078', '10071', '10059', '10382', '10297', '10294', '10293', '8961', '8962', '10250', '9473', '8965', '9888', '9491', '9525', '10209', '9145', '9714', '10335', '10336', '9211', '9127', '9212', '8880', '10227', '10226', '10222', '10221', '10219', '10217', '9438', '9896', '9515', '9513', '9512', '9489', '8924', '9563', '9562', '9577', '10122', '8816', '8812', '8811', '8813', '8815', '10159', '10162', '9160', '9158', '9157', '9176', '9174', '9171', '9268', '9102', '9275', '9642', '9944', '9580', '9559', '9775', '9418', '9970', '9122', '9915', '9210', '9108', '10133', '8862', '8861', '9373', '9136', '9107', '10304', '9397', '9699', '9485', '9486', '9700', '9487', '9698', '9488', '10100', '9619', '9213', '10029', '9455', '9104', '9752', '9980', '9153', '9155', '9152', '9151', '9150', '9149', '10036', '9641', '9374', '9776', '9130', '9131', '8936', '8935', '8932', '10002', '10143', '10142', '9918', '9119', '9121', '9901', '9490', '8938', '8939', '10289', '9897', '10047', '9457', '9542', '9543', '9180', '9178', '9179', '9177', '8944', '8945', '8946', '8947', '8948', '8949', '8950', '9000', '9003', '9006', '9050', '9054', '9156', '9161', '9183', '9053', '9055', '9835', '9836', '9837', '8982', '9926', '9927', '9929', '9928', '9639', '9638', '9230', '9092', '9410', '9900', '9602', '9603', '9604', '10030', '9267', '9911', '9909', '9910', '10249', '10273', '10240', '9640', '9253', '10330', '10331', '9112', '9117', '9118', '9682', '9976', '9175', '9791', '9270', '9271', '9594', '10134', '9734', '9733', '9692', '10033', '10314', '9244', '9950', '9943', '9898', '9059', '9925', '9687', '9219', '9376', '9058', '9852', '9867', '9816', '9201', '9665', '9792', '9793', '9841', '9741', '10327', '10001', '9214', '9088', '9807', '9076', '9075', '9074', '9073', '10311', '9942', '10118', '9096', '8978', '8977', '8975', '9955', '9818', '9770', '9111', '9126', '9678', '9981', '9982', '10279', '10280', '10281', '10282', '10177', '10186', '8993', '9592', '9590', '9591', '9586', '9585', '9582', '9008', '10375', '9702', '9056', '9993', '9988', '9989', '9990', '9460', '9461', '9462', '9463', '9465', '9466', '9467', '9468', '9469', '9471', '10389', '10390', '10379', '10380', '8790', '9833', '9527', '9167', '9168', '9264', '9265', '9072', '9071', '10127', '10043', '10042', '10040', '10039', '9742', '9876', '9875', '9023', '9877', '10363', '10361', '10038', '9202', '9949', '9497', '10278', '10268', '10091', '10011', '9593', '9596', '9595', '9042', '9552', '9553', '10027', '9234', '9235', '9236', '9239', '9238', '9237', '10116', '10115', '8941', '10046', '9040', '9605', '9861', '9521', '8929', '8976', '9647', '10145', '9996', '9997', '9693', '9684', '9685', '9691', '9760', '9761', '9780', '9781', '9782', '9783', '9784', '9069', '9932', '9899', '10008', '10019', '10021', '9464', '8796', '9560', '9574', '9614', '9814', '9887', '9774', '9172', '9892', '10105', '9953', '9956', '9246', '9759', '9769', '9772', '8960', '9987', '9021', '9879', '9880', '9878', '9617', '9070', '10296', '8979', '8998', '8985', '9085', '9245', '9066', '10006', '10004', '9484', '9481', '10077', '9798', '9623', '9019', '9045', '9827', '9828', '9830', '9044', '9043', '9041', '9191', '10114', '10074', '10073', '10072', '9399', '9400', '9401', '9402', '9403', '9404', '9204', '9133', '10052', '9408', '9478', '9840', '8895', '9139', '9386', '9857', '9858', '9902', '9916', '9964', '9966', '9967', '9968', '9249', '9248', '9263', '9885', '9806', '9146', '9147', '9148', '9398', '9259', '9256', '9391', '9170', '9372', '9123', '9124', '9514', '9432', '9433', '9379', '9523', '9894', '9890', '9868', '9869', '9870', '9812', '9415', '9261', '9260', '9262', '10135', '10137', '9532', '9278', '9526', '9848', '9566', '9884', '9435', '9436', '9437', '9668', '9667', '9666', '9387', '9703', '10332', '10117', '9474', '9476', '9655', '9475', '9838', '9493', '9166', '9164', '9163', '9165', '9162', '9115', '9113', '10045', '9862', '9502', '9674', '9637', '9704', '9615', '9622', '9628', '9652', '10276', '9796', '9832', '9933', '9983', '9984', '9985', '10090', '9722', '9846', '9708', '9712', '10253', '10259', '10260', '9715', '9749', '9883', '8923', '9743', '9860', '10007', '9804', '9903', '10267', '9809', '10215', '10216', '10214', '10213', '9863', '9920', '10263', '10264', '9881', '9906', '9907', '9908', '9923', '8984', '9009', '9010', '9062', '9063', '10284', '9948', '9922', '9921', '9931', '10290', '10016', '10211', '10358', '10310', '10309', '10308', '10307', '10012', '10013', '10014', '10015', '10305', '10088', '10054', '10032', '10355', '10034', '10035', '10124', '10126', '10110', '10104', '10299', '10136', '10274', '10093', '10107', '10108', '10109', '10312', '10328', '10329', '10202', '10204', '10119', '10121', '10125', '10141', '10140', '10139', '10138', '10146', '10149', '10208', '10151', '10201', '10207', '10295', '10288', '10315', '10352', '10353', '10356', '10373', '10365', '10369', '10381', '9060', '9817', '10238', '10237', '10236', '10235', '10234', '10231', '10230', '10229', '10228', '10225', '10224', '10223', '10041', '9492', '9494', '9280', '9534', '9958', '9960', '9959', '9961', '8994', '8992', '9882', '8991', '9721', '9720', '9719', '9718', '9717', '9716', '8995', '8989', '8988', '8971', '8970', '8969', '8968', '8967', '9986', '10132', '9132', '9089', '9951', '9886', '9225', '9226', '9227', '9367', '9272', '10144', '9423', '9856', '9767', '9766', '9765', '9764', '9763', '9762', '9101', '9522', '8937', '9392', '9393', '10010', '9565', '9572', '10018', '9758', '10271', '10270', '10269', '9745', '10360', '9738', '9737', '9746', '9431', '9443', '9430', '9429', '9169', '9663', '10176', '9091', '9090', '10028', '10175', '10210', '9095', '9620', '9740', '9182'
]

# Output file names
OUTPUT_EXCEL_FILE = "job_portal_extracted_details.xlsx"
OUTPUT_CSV_FILE = "job_portal_extracted_details.csv" # New CSV output file

# --- Main Script ---
def extract_job_details():
    # Initialize WebDriver with options that worked previously
    options_for_manual_login = webdriver.ChromeOptions()
    # This option suppresses the "DEPRECATED_ENDPOINT" and other console logs from Chrome
    options_for_manual_login.add_experimental_option('excludeSwitches', ['enable-logging']) 
    # DO NOT add --headless here if you need to manually solve reCAPTCHA
    driver = webdriver.Chrome(options=options_for_manual_login) # Reverted to this initialization

    all_job_data = [] # To store data for Excel export

    try:
        print(f"Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)

        # --- Login ---
        print("Waiting for login elements...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(USERNAME)

        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        print("\n--- ATTENTION: reCAPTCHA/Manual Login Required ---")
        print("Please manually complete the login process in the opened browser window.")
        print("Solve any reCAPTCHA and click the 'Sign In' button.")
        print("The script will wait for the URL to change, indicating successful login.")

        WebDriverWait(driver, 600).until( # Increased timeout to 10 minutes for manual intervention
            EC.url_changes(LOGIN_URL)
        )
        print("Logged in successfully (URL changed). Resuming script.")
        time.sleep(2) # Small pause after login for good measure

        # --- Iterate through provided Job Codes ---
        print(f"Starting to fetch details for {len(job_codes)} jobs...")
        for i, code in enumerate(job_codes):
            job_url = BASE_JOB_URL.format(code)
            print(f"\nProcessing Job {i+1}/{len(job_codes)} (Code: {code}): {job_url}")
            
            try:
                driver.get(job_url)
                # Wait for a key element on the job page to load, like the company name
                # Using a more robust wait for the company name element
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h4.panel-title.pt-4"))
                )
                time.sleep(2) # Additional short pause to ensure all content renders

                # Get the full page source after dynamic content loads
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Initialize values
                company_name = "N/A"
                job_role = "N/A"
                job_type = "N/A"
                cpi_cutoff = "N/A"
                allow_bonus_applications = "N/A"
                btech_gross_salary = "N/A"
                btech_ctc = "N/A"

                # 1. Extract Company Name (using user's specific class)
                company_elem = soup.find("h4", class_="panel-title pt-4")
                if company_elem:
                    company_name = company_elem.get_text(strip=True)
                    print(f"  Company: {company_name}")

                # 2. Extract Job Role (using user's specific class)
                job_role_elem = soup.find("h2", class_="panel-title")
                if job_role_elem:
                    job_role = job_role_elem.get_text(strip=True)
                    print(f"  Job Role: {job_role}")

                # 3. Extract Job Type (using user's specific class)
                job_type_elem = soup.find(class_="job-designation") # Search for any tag with this class
                if job_type_elem:
                    job_type = job_type_elem.get_text(strip=True)
                    print(f"  Job Type: {job_type}")

                # 4. Extract CPI Cutoff and Allow Bonus Applications
                # Find the parent div with class="mt-3"
                info_div = soup.find('div', class_='mt-3')
                if info_div:
                    h4_tags = info_div.find_all('h4')
                    for h4 in h4_tags:
                        text = h4.get_text(strip=True)
                        if text.startswith("CPI Cutoff:"):
                            match = re.search(r'CPI Cutoff:\s*(.*)', text)
                            if match:
                                cpi_cutoff = match.group(1).strip()
                            print(f"  CPI Cutoff: {cpi_cutoff}")
                        elif text.startswith("Allow bonus applications:"):
                            match = re.search(r'Allow bonus applications:\s*(.*)', text)
                            if match:
                                allow_bonus_applications = match.group(1).strip()
                            print(f"  Allow Bonus Applications: {allow_bonus_applications}")
                else:
                    print("  Info div (class='mt-3') not found for CPI/Bonus.")


                # 5. Extract B.Tech Gross Salary and CTC from the table
                salary_table = soup.find("table") # Assuming there's only one main table or this is the correct one
                if salary_table:
                    headers = [th.get_text(strip=True) for th in salary_table.find_all("th")]
                    
                    # Find column indices
                    try:
                        program_idx = headers.index("Program")
                        gross_salary_idx = headers.index("Gross salary")
                        ctc_idx = headers.index("CTC")
                    except ValueError as ve:
                        print(f"  Warning: Missing expected header in salary table: {ve}")
                        program_idx, gross_salary_idx, ctc_idx = -1, -1, -1 # Mark as not found

                    if program_idx != -1 and gross_salary_idx != -1 and ctc_idx != -1:
                        # Iterate through table rows (skip header row if necessary, find all tr)
                        for row in salary_table.find_all("tr"):
                            cols = row.find_all("td")
                            # Ensure row has enough columns
                            if len(cols) > max(program_idx, gross_salary_idx, ctc_idx):
                                program_text = cols[program_idx].get_text(strip=True)
                                
                                # Check if this is the B.Tech row
                                if program_text.lower() == "b.tech.": # Using .lower() for robustness
                                    btech_gross_salary = cols[gross_salary_idx].get_text(strip=True).replace(',', '')
                                    btech_ctc = cols[ctc_idx].get_text(strip=True).replace(',', '')
                                    print(f"  B.Tech Gross Salary: {btech_gross_salary}")
                                    print(f"  B.Tech CTC: {btech_ctc}")
                                    break # Found B.Tech row, no need to search further
                    else:
                        print("  Could not find all necessary salary table headers (Program, Gross salary, CTC).")
                else:
                    print("  Salary table not found on the page.")

                # Store extracted data
                all_job_data.append({
                    "Job Code": code,
                    "Company Name": company_name,
                    "Job Role": job_role,
                    "Job Type": job_type,
                    "CPI Cutoff": cpi_cutoff,
                    "Allow Bonus Applications": allow_bonus_applications,
                    "B.Tech Gross Salary": btech_gross_salary,
                    "B.Tech CTC": btech_ctc
                })

            except Exception as e:
                print(f"  Error processing Job Code {code}: {e}")
                # Append partial data or error indicators for failed extractions
                all_job_data.append({
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
            
            time.sleep(1) # Be polite, add a small delay between requests

    except Exception as e:
        print(f"\nAn error occurred during the main scraping process: {e}")
    finally:
        driver.quit() # Always close the browser when done

    # --- Create DataFrame and Export to Excel ---
    if all_job_data:
        df = pd.DataFrame(all_job_data)
        
        # OPTION 1: Save to XLSX using xlsxwriter engine (Recommended first try for .xlsx)
        # You might need to install xlsxwriter: pip install xlsxwriter
        try:
            df.to_excel(OUTPUT_EXCEL_FILE, index=False, engine='xlsxwriter')
            print(f"\nSuccessfully saved data to '{OUTPUT_EXCEL_FILE}' using xlsxwriter engine.")
        except Exception as e:
            print(f"\nError saving to XLSX with xlsxwriter: {e}")
            print("Attempting to save with default engine...")
            df.to_excel(OUTPUT_EXCEL_FILE, index=False) # Fallback to default engine
            print(f"Successfully saved data to '{OUTPUT_EXCEL_FILE}' using default engine.")

        # OPTION 2: Save to CSV with UTF-8 BOM encoding (Most robust for Excel import)
        # This creates a CSV file that Excel can usually open correctly without character issues.
        # You will need to import this CSV into Excel using the "Data" tab -> "From Text/CSV" option.
        try:
            df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8-sig')
            print(f"Also saved data to '{OUTPUT_CSV_FILE}' with UTF-8 BOM encoding.")
            print("If you see garbled characters in the XLSX, try opening the CSV file in Excel via 'Data > From Text/CSV' and select 'UTF-8' as the file origin.")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    else:
        print("\nNo job data was extracted to write to Excel or CSV.")

# Run the script
if __name__ == "__main__":
    extract_job_details()
