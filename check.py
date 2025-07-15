



# df = pd.read_csv("raw_jds_summary.csv")

# df = df.rename(columns={'Raw_JD_Text_Snippet':'Raw_JD_Text_Summary'})  

import pandas as pd
import os
from pathlib import Path

def merge_text_files_with_excel(excel_file_path, text_files_folder, job_code_column, output_file_path=None):
    """
    Merge text files content into Excel sheet based on job codes.
    
    Parameters:
    excel_file_path (str): Path to the Excel file
    text_files_folder (str): Path to folder containing text files
    job_code_column (str): Name of the column containing job codes
    output_file_path (str): Path for output file (optional, defaults to input file with '_updated' suffix)
    """
    
    try:
        # Read the Excel file
        df = pd.read_csv(excel_file_path)
        print(f"Successfully loaded Excel file with {len(df)} rows")
        
        # Check if job code column exists
        if job_code_column not in df.columns:
            print(f"Error: Column '{job_code_column}' not found in Excel file")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Create a new column for text content
        df['Text_Content'] = ''
        
        # Convert folder path to Path object
        folder_path = Path(text_files_folder)
        
        if not folder_path.exists():
            print(f"Error: Folder '{text_files_folder}' does not exist")
            return
        
        # Counter for successful matches
        matched_count = 0
        not_found_count = 0
        
        # Process each row
        for index, row in df.iterrows():
            job_code = str(row[job_code_column]).strip()
            
            # Skip if job code is empty or NaN
            if pd.isna(job_code) or job_code == '' or job_code == 'nan':
                continue
            
            # Construct the expected filename
            filename = f"NA_NA_{job_code}.txt"
            file_path = folder_path / filename
            
            # Check if file exists and read content
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        df.at[index, 'Text_Content'] = content
                        matched_count += 1
                        print(f"✓ Matched: {filename}")
                except Exception as e:
                    print(f"✗ Error reading {filename}: {e}")
            else:
                not_found_count += 1
                print(f"✗ File not found: {filename}")
        
        # Generate output file path if not provided
        if output_file_path is None:
            input_path = Path(excel_file_path)
            output_file_path = input_path.parent / f"{input_path.stem}_updated{input_path.suffix}"
        
        # Save the updated Excel file
        df.to_excel(output_file_path, index=False)
        
        print(f"\n=== SUMMARY ===")
        print(f"Total rows processed: {len(df)}")
        print(f"Files found and matched: {matched_count}")
        print(f"Files not found: {not_found_count}")
        print(f"Updated file saved as: {output_file_path}")
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def list_text_files_in_folder(folder_path):
    """
    Helper function to list all text files in the folder to verify naming pattern
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder '{folder_path}' does not exist")
        return
    
    txt_files = list(folder.glob("*.txt"))
    print(f"\nFound {len(txt_files)} text files:")
    for file in txt_files[:10]:  # Show first 10 files
        print(f"  - {file.name}")
    
    if len(txt_files) > 10:
        print(f"  ... and {len(txt_files) - 10} more files")

# Example usage
if __name__ == "__main__":
    # Update these paths according to your setup
    excel_file = "raw_jds_summary.csv"  # Replace with your Excel file path
    text_folder = "fetched_jds"  # Replace with your text files folder path
    job_column = "Job_Code"  # Replace with your actual job code column name
    
    # Optional: List files in folder to verify naming pattern
    print("=== CHECKING TEXT FILES ===")
    list_text_files_in_folder(text_folder)
    
    print("\n=== MERGING FILES ===")
    # Run the merge function
    result = merge_text_files_with_excel(
        excel_file_path=excel_file,
        text_files_folder=text_folder,
        job_code_column=job_column
    )
    
    if result is not None:
        print("\n=== PREVIEW OF UPDATED DATA ===")
        print(result.head())