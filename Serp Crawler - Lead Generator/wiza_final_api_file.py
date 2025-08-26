import json
import requests
import pandas as pd
import time
import logging
import subprocess
import os
import json
base_path = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

with open(r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\Xoinx Serp Crawling GUI\wiza_inputs.json", "r") as f:
    wiza_gui_api_data = json.load(f)

company_location = wiza_gui_api_data.get("company_location") or None
company_industry = wiza_gui_api_data.get("company_industry") or None
company_size = wiza_gui_api_data.get("company_size") or None
revenue = wiza_gui_api_data.get("revenue") or None
job_title_level = wiza_gui_api_data.get("job_title_level") or None
job_role = wiza_gui_api_data.get("job_role") or None
job_sub_role = wiza_gui_api_data.get("job_sub_role") or None
job_title_text_input = wiza_gui_api_data.get("job_title", [None])[0]

def headers_and_api_key():
    master_api_key = "fa70328228bcaafda950fa1c03d24a09269d8c5d6effdc6354cd9c5421e23008"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {master_api_key}"
    }
    return headers


def checking_if_contacts_exist(lst, api):
    global results
    prospect_search_url = "https://wiza.co/api/prospects/search"
    results = {}
    
    payloads = [
        {
            "filters": {
                "job_company": [{"v": None, "s": "i"}],
                "job_title_level": [job_title_level] if job_title_level else [],
                "company_location": [{"v": company_location, "b": "state", "s": "i"}] if company_location else [{"v": None, "b": "state", "s": "i"}],
                "company_industry": [company_industry],
                "company_size": [company_size], 
                "revenue": [revenue],
                "job_role":[job_role],
                "job_sub_role": [job_sub_role],
                "job_title": [
                {"v": job_title_text_input, "s": "i"}]

            }
        },
        {## Drop Industry, Company Size, and Revenue
            "filters": {
                "job_company": [{"v": None, "s": "i"}],
                "job_title_level": [job_title_level] if job_title_level else [],
                "company_location": [{"v": company_location, "b": "state", "s": "i"}] if company_location else [{"v": None, "b": "state", "s": "i"}],
                "job_role":[job_role],
                "job_sub_role": [job_sub_role],
                "job_title": [
                {"v": job_title_text_input, "s": "i"}]

            }
        },
        {## Drop Industry, Company Size, and Revenue, Inputted job role, and subrole
            "filters": {
                "job_company": [{"v": None, "s": "i"}],
                "job_title_level": [job_title_level] if job_title_level else [],
                "company_location": [{"v": company_location, "b": "state", "s": "i"}] if company_location else [{"v": None, "b": "state", "s": "i"}],
                "job_role":[job_role],

            }
        },
        {## Drop Industry, Company Size, and Revenue, Inputted job role, and subrole, job_titles and job role, just search location
            "filters": {
                "job_company": [{"v": None, "s": "i"}],
                "company_location": [{"v": company_location, "b": "state", "s": "i"}] if company_location else [{"v": None, "b": "state", "s": "i"}],

            }
        }]

    for domain in lst:
        inner_results = {}
        try:
            total_contacts = 0
            for idx, payload_template in enumerate(payloads):
                payload_template["filters"]["job_company"][0]["v"] = domain
                payload = json.dumps(payload_template)

                response = requests.post(prospect_search_url, headers=api, data=payload, timeout=10)
                
                if response.status_code == 200:
                    total_returned = response.json()
                    if 'data' in total_returned and 'total' in total_returned['data']:
                        total_contacts = int(total_returned['data']['total'])
                    else:
                        continue
                    
                    if total_contacts > 0:
                        inner_results = {"total_contacts": total_contacts, "payload": payload}
                        print(f"Found on payload {idx + 1} for {domain}")
                        break  
                else:

                    inner_results = {"error": f"Status code {response.status_code}"}
                    continue

            if total_contacts == 0 and "error" not in inner_results:
                inner_results = {"total_contacts": 0, "payload": None}
                print(f"No Contacts for {domain}")
            results[domain] = inner_results

        except Exception as e:

            results[domain] = {"error": str(e)}

    return results


def create_prospect_lists_costs(lst, api):
    global lst_of_people_ids
    wiza_send_cost_request = "https://wiza.co/api/prospects/create_prospect_list"
    lst_of_people_ids = []
    
    for domain, data in lst.items():
        try:

            if data.get("error"):
                print(f"Skipping {domain} due to pre-existing error: {data['error']}")
                continue

            if not data.get("payload"):
                print(f"Skipping {domain} due to missing or None payload.")
                continue

            try:
                filters = json.loads(data["payload"])["filters"]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Invalid payload for {domain}: {e}")
                continue

            payload = json.dumps({
                "filters": filters,
                "list": {
                    "name": f"Prospects for {domain}",
                    "max_profiles": 1,
                    "enrichment_level": "full"
                }
            })

            response = requests.post(wiza_send_cost_request, headers=api, data=payload, timeout=15) 
            response.raise_for_status()
            response_data = response.json()

            job_id = response_data.get('data', {}).get('id')
            if job_id:
                lst_of_people_ids.append({"domain": domain, "job_id": job_id})
                print(f"Sending {domain} for $ Scrap")
            else:
                print(f"No job_id returned for {domain}: {response_data}")

            time.sleep(4)  

        except requests.exceptions.RequestException as e:
            print(f"HTTP error for {domain}: {e}")
            time.sleep(60) 
            continue

    return lst_of_people_ids


def print_check_sent_jobs(sending_job, api):

    global completed_jobs
    completed_jobs = [] 

    while sending_job:  
        for job in sending_job:  
            job_id = job['job_id']
            url = f"https://wiza.co/api/lists/{job_id}"

            try:
                response = requests.get(url, headers=api, timeout=4)
                response.raise_for_status()
                data = response.json()

                status = data['data']['status']
                domain_name = data['data']['name']

                if status == "finished":
                    time_finished = data['data']['finished_at']
                    print(f"The company {domain_name} has finished at {time_finished}")
                    completed_jobs.append(job)  
                    sending_job.remove(job)  
                else:
                    print(f"The company {domain_name} is still {status}. Skipping for now...")

            except requests.exceptions.RequestException as e:
                print(f"Error checking status for job {e}")
                time.sleep(10) 
                continue

        print("Checking all pending jobs again in 7 seconds...")
        time.sleep(7)  

    return completed_jobs  


def collecting_all_data_into_df(lst, api):
    all_dfs = []
    
    for job in lst:
        try:
            job_id = job.get('job_id')
            if not job_id:
                logging.warning(f"Skipping job with missing job_id: {job}")
                continue
            
            url = f"https://wiza.co/api/lists/{job_id}/contacts?segment=people"
            response = requests.get(url, headers=api, timeout=4)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list) and data['data']:
                df_temp = pd.json_normalize(data['data'])
                all_dfs.append(df_temp)
                logging.info(f"Data collected for job_id {job_id}")
            else:
                logging.warning(f"No valid data found for job_id {job_id}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for job_id {job_id}: {e}")
            time.sleep(5)  
            continue
        except Exception as e:
            logging.error(f"Error processing job_id {job_id}: {e}")
            continue

    if all_dfs:
        all_dfs = [df for df in all_dfs if not df.empty]
        if all_dfs:
            all_conacts_df_final = pd.concat(all_dfs, ignore_index=True)
            all_conacts_df_final.to_csv(os.path.join(base_path, "final_wiza_saved_data.csv"), index=False)
            return all_conacts_df_final
    
    logging.warning("No data collected. Returning an empty DataFrame.")
    return pd.DataFrame()


def get_api_credits(headers):
    url = "https://wiza.co/api/meta/credits"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        credits = data['credits']['api_credits']
        return print(f"Total Credits Left: {credits}")
    else:
        print(f"Error: Unable to fetch credits. Status code: {response.status_code}")
        return None


def main():
    try:
        domains_df = pd.read_csv(os.path.join(base_path, "target_domains.csv"))
        domains_df['Domain'] = domains_df['Domain'].str.strip()
        domains = domains_df['Domain'].to_list()
        logging.info("Domains defined.")

        api = headers_and_api_key()
        logging.info("API headers retrieved.")
        if domains:  # Check if domains list is not empty
            if len(domains) < 1000:
                try:
                    check_if_contact_exist = checking_if_contacts_exist(domains[0:20], api) ## Change this here as needed
                    logging.info("Checked for existing contacts.")
                except Exception as e:
                    logging.error(f"Error checking contacts: {e}")
            else:
                logging.info("Domain count exceeds 500. Skipping contact check.")
        else:
            logging.warning("No domains found in the input file.")

        sending_prospect_lst = create_prospect_lists_costs(check_if_contact_exist, api)
        logging.info("Prospect lists created.")

        completed_jobs = print_check_sent_jobs(sending_prospect_lst, api)
        logging.info("Job statuses checked. Completed jobs retrieved.")
        print(f"Completed jobs: {completed_jobs}")

        df = collecting_all_data_into_df(completed_jobs, api)
        logging.info("Data collected into DataFrame.")

        credits_left = get_api_credits(api) 
        print(credits_left)
        print(f"Total Contacts Found: {len(df)}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    df = main()

