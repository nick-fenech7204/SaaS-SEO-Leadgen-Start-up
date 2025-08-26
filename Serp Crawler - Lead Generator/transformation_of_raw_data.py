import pandas as pd
import requests
import time
from pandas import json_normalize
import subprocess
import os
base_path = os.path.dirname(__file__)


# Constants
API_TOKEN = 'blank'
API_URL_PATTERN = 'https://api.serpstat.com/v{version}?token={token}'
API_URL = API_URL_PATTERN.format(version=4, token=API_TOKEN)
INPUT_PATH = os.path.join(base_path, "raw_serp_data.csv")
# INPUT_PATH = r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\GUI\raw_serp_data.csv"
MAX_RETRIES = 5
RETRY_DELAY = 5
BATCH_SIZE = 10
CLASSIFICATION_BATCH_SIZE = 1000

# Initialize session
session = requests.Session()

def load_and_preprocess_data(input_path):
    global df_serp_data
    try:
        df_serp_data = pd.read_csv(input_path) 
        df_filtered = df_serp_data[(df_serp_data['position'] >= 5) & (df_serp_data['position'] <= 30)]
        unique_domains = df_filtered['domain'].drop_duplicates().to_list()
        print(f"Total Amount going for Domain Data: {len(unique_domains)}")
        return df_filtered, unique_domains
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        raise


# Function to split a list into batches
def split_into_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

# Function to make a request with retries
def make_request(session, url, data, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            resp = session.post(url, json=data)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 504:
                print(f"504 Gateway Timeout. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    raise Exception(f"Failed after {retries} retries")

# Function to process domains in batches
def process_domains_in_batches(domains, session, api_url, batch_size):
    all_data = []
    for domain_batch in split_into_batches(domains, batch_size):
        data = {
            "id": "1",
            "method": "SerpstatDomainProcedure.getDomainsInfo",
            "params": {
                "domains": domain_batch,
                "se": "g_us",  # Search engine
                "filters": {}
            }
        }
        try:
            result = make_request(session, api_url, data)
            all_data.extend(result['result']['data']) 
            print(f"Processed batch of size {len(domain_batch)}. Total records: {len(all_data)}")
            time.sleep(3)  # Avoid hitting rate limits
        except Exception as e:
            print(f"Error processing batch {domain_batch}: {e}")
    return all_data

# Function to add a classification task
def add_classification_task(domains_batch):
    payload = {
        "method": "DomainClassification.addTask",
        "id": 1,
        "params": {
            "domains": domains_batch
        }
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if "result" in response_data and "task_id" in response_data["result"]:
            return response_data["result"]["task_id"]
    raise Exception(f"Error adding classification task: {response.json()}")

# Function to fetch task results
def fetch_task_results(task_id):
    while True:
        payload = {
            "method": "DomainClassification.getTask",
            "id": 1,
            "params": {
                "task_id": task_id
            }
        }
        response = requests.post(API_URL, json=payload)
        response_data = response.json()
        if response.status_code == 200 and "result" in response_data:
            result = response_data["result"]
            if result.get("data") is None and result.get("status") == "1":
                print(f"Task {task_id} is still pending. Retrying in 30 seconds...")
                time.sleep(30)
            else:
                return result
        else:
            raise Exception(f"Error fetching task results: {response_data}")

# Function to save the DataFrame to a file
def save_dataframe(df, output_path, description):
    try:
        df.to_csv(output_path, index=False)
        print(f"{description} saved to {output_path}")
    except Exception as e:
        print(f"Error saving {description}: {e}")

# Main process
def main():
    try:
        # Load and preprocess data
        raw_data_df, unique_domains = load_and_preprocess_data(INPUT_PATH)

        tabular_data = process_domains_in_batches(unique_domains, session, API_URL, BATCH_SIZE)
        all_api_data_df = pd.json_normalize(tabular_data)
        raw_data_from_serp_crawl_path = pd.merge(df_serp_data, all_api_data_df, on='domain', how='left')
        all_api_data_output_path = os.path.join(base_path, "all_unfiltered_transformed_data.csv")
        # all_api_data_output_path = r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\GUI\all_unfiltered_transformed_data.csv"
        save_dataframe(raw_data_from_serp_crawl_path, all_api_data_output_path, "All API data (unfiltered)")

        # Filter domains for classification
        big_player_exclude_df = all_api_data_df[
            (all_api_data_df['keywords'] <= 7000) & 
            (all_api_data_df['traff'] <= 70000) & 
            (all_api_data_df['ads'] == 0)]
        
        big_player_exclude_list = big_player_exclude_df['domain'].to_list()

        # Process classification tasks
        all_results = []
        for i in range(0, len(big_player_exclude_list), CLASSIFICATION_BATCH_SIZE):
            batch = big_player_exclude_list[i:i + CLASSIFICATION_BATCH_SIZE]
            task_id = add_classification_task(batch)
            result_data = fetch_task_results(task_id)
            all_results.extend(result_data.get("data", []))

        # Prepare classification results DataFrame
        rows = [
            [result["domain"], ", ".join(result.get("categories_names", []))]
            for result in all_results
        ]
        classified_domains_df = pd.DataFrame(rows, columns=["Domain", "Industries"])
        classified_domains_df['Industries'] = classified_domains_df['Industries'].str.replace('/', ', ')

        # Save filtered and classified data
        classified_data_output_path = os.path.join(base_path, "target_domains.csv")
        # classified_data_output_path = r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\GUI\target_domains.csv"
        save_dataframe(classified_domains_df, classified_data_output_path, "Filtered and classified data")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()

