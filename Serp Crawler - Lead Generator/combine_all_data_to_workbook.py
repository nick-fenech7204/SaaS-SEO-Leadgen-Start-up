import pandas as pd
import logging
import os
from datetime import datetime  # Import datetime

base_path = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_csvs_to_excel(output_excel_path):
    try:
        file_paths = {
            "Raw Data": os.path.join(base_path, "all_unfiltered_transformed_data.csv"),
            "Domains": os.path.join(base_path, "target_domains.csv"),
            "Wiza": os.path.join(base_path, "final_wiza_saved_data.csv")
        }

        with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
            for sheet_name, file_path in file_paths.items():
                try:
                    df = pd.read_csv(file_path)

                    # Preprocess URLs to prevent hyperlinking
                    for col in df.select_dtypes(include='object').columns:
                        if df[col].str.contains(r'http[s]?://', na=False).any():
                            df[col] = df[col].apply(lambda x: f"URL: {x}" if isinstance(x, str) and x.startswith(('http://', 'https://')) else x)

                    # Write the modified DataFrame to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    print(f"Added {sheet_name} to {output_excel_path}")
                except Exception as e:
                    print(f"Error processing {sheet_name}: {e}")
        print(f"All files saved to {output_excel_path} successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Generate timestamped filename
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
output_excel_path = os.path.join(downloads_folder, f"final_serp_crawl_workbook_{current_time}.xlsx")

save_csvs_to_excel(output_excel_path)
