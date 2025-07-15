import os
import pandas as pd
import json
import asyncio
import time
import re
import openai

# --- CONFIG ---
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...ngUA")
MODEL = "gpt-4o"

INPUT_JDS_DIR = "test_jds"
OUTPUT_EXCEL_FILE = "Job_Roles_Parsed_OpenAI.xlsx"
CONCURRENT_CALLS = 5
MAX_RETRIES = 2
RETRY_DELAY = 5

PROMPT_TEMPLATE = """
Extract key job information from the following Job Description.

Return a single valid JSON object only. Do not include any extra text or markdown. Use this format:

{{
  "Company": "",
  "Role": "",
  "Eligibility": "",
  "Location": "",
  "Key Skills": [],
  "Key Keywords": [],
  "Project Ideas/Relevant Projects": [],
  "Assessment Rounds": "",
  "Unique Requirements": "",
  "Company Description Insights": "",
  "Job_Code": "{job_code}",
  "Original_File": "{file_name}"
}}

If a value is completely missing, return "N/A". Otherwise infer intelligently.

Job Description:
{jd_text}
"""


semaphore = asyncio.Semaphore(CONCURRENT_CALLS)

def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()

async def call_openai_api(prompt, file_name):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with semaphore:
                response = await openai.ChatCompletion.acreate(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                content = response.choices[0].message["content"]
                print(f"\n📦 Raw LLM Response for {file_name}:\n{content[:500]}...\n")

                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if not json_match:
                    raise ValueError("No JSON found in response.")
                return json.loads(json_match.group(0))

        except Exception as e:
            print(f"[{file_name}] Attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
    return {}

async def process_file(file_name):
    file_path = os.path.join(INPUT_JDS_DIR, file_name)
    job_code = file_name.split('_')[-1].replace('.txt', '')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_name}: {e}")
        return default_entry("FILE_ERROR", file_name, job_code)

    if len(raw_text.strip()) < 30:
        print(f"⚠️ Skipping {file_name} — JD too short.")
        return default_entry("TOO_SHORT", file_name, job_code)

    prompt = PROMPT_TEMPLATE.format(
        jd_text=clean_text(raw_text),
        job_code=job_code,
        file_name=file_name
    )
    result = await call_openai_api(prompt, file_name)

    return {
        "Company": result.get("Company", "N/A"),
        "Role": result.get("Role", "N/A"),
        "Eligibility": result.get("Eligibility", "N/A"),
        "Location": result.get("Location", "N/A"),
        "Key Skills": result.get("Key Skills", []),
        "Key Keywords": result.get("Key Keywords", []),
        "Project Ideas/Relevant Projects": result.get("Project Ideas/Relevant Projects", []),
        "Assessment Rounds": result.get("Assessment Rounds", "N/A"),
        "Unique Requirements": result.get("Unique Requirements", "N/A"),
        "Company Description Insights": result.get("Company Description Insights", "N/A"),
        "Job_Code": job_code,
        "Original_File": file_name
    }

def default_entry(reason, file_name, job_code):
    return {
        "Company": reason, "Role": reason, "Eligibility": reason,
        "Location": reason, "Key Skills": [], "Key Keywords": [],
        "Project Ideas/Relevant Projects": [], "Assessment Rounds": reason,
        "Unique Requirements": reason, "Company Description Insights": reason,
        "Job_Code": job_code, "Original_File": file_name
    }

async def main():
    files = [f for f in os.listdir(INPUT_JDS_DIR) if f.endswith('.txt')]
    print(f"📄 Found {len(files)} files.")
    tasks = [process_file(f) for f in files]
    results = await asyncio.gather(*tasks)

    df = pd.DataFrame(results)
    for col in ["Key Skills", "Key Keywords", "Project Ideas/Relevant Projects"]:
        df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    column_order = [
        "Company", "Role", "Eligibility", "Location", "Key Skills",
        "Key Keywords", "Project Ideas/Relevant Projects", "Assessment Rounds",
        "Unique Requirements", "Company Description Insights", "Job_Code", "Original_File"
    ]
    df = df.reindex(columns=column_order)
    df.to_excel(OUTPUT_EXCEL_FILE, index=False)
    print(f"\n✅ Done! Output saved to {OUTPUT_EXCEL_FILE}")

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\n⏱️ Finished in {time.time() - start:.2f}s")
