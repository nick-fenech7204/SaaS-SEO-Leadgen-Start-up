import pandas as pd
import re
import os
import time
import random
import numpy as np
from datetime import datetime
import pandas as pd
import requests
from pandas import json_normalize
from time import sleep
from datetime import datetime
import subprocess
import os
base_path = os.path.dirname(__file__) 


current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H-%M-%S")

api_token = 'f359ba3b7fd13d62a7fd6aa576c260bd'                                                         
api_url_pattern = 'https://serpstat.com/rt/api/v{version}?token={token}'
api_url = api_url_pattern.format(version=2, token=api_token)
file_path_new_task_ids = os.path.join(base_path, "current_task_ids.txt")
path_for_location_excel = os.path.join(base_path, "Location Table.xlsx")
# file_path_new_task_ids = r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\GUI\current_task_ids.txt" ### Change Path Here
# path_for_location_excel = r"C:\Users\nickj\OneDrive\Desktop\Xoinx\Code\GUI\Location Table.xlsx" ### Change Path Here
locations_full_df = pd.read_excel(path_for_location_excel, sheet_name ='data_to_query' )
locations_full_df.rename(columns={'SerpStat ID' : 'region_id', "State Name" : "region_state", "Location Name" : "region_name"}, inplace=True)

lst_of_keyword_data = []
full_df_data = []

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": f"{api_token}",
}


data_for_get_list = {
  "id": 1,
  "method": "tasks.getList",
  "params": {
       "page": 1,
       "pageSize": 1000
    }
}

resp_get_list = requests.post(api_url, json=data_for_get_list, headers=headers)
lst_of_serped_tasks = resp_get_list.json()
unclean_df_get_list = lst_of_serped_tasks['result']
df_get_list = pd.DataFrame.from_records(unclean_df_get_list)
df_get_list['task_id'] = df_get_list['task_id'].astype(int)

lst_of_all_tsk_ids = df_get_list['task_id'].to_list()

try:
    with open(file_path_new_task_ids, "r") as file:
        # Parse each line into task ID and industry
        task_industry_pairs = [
            line.strip().split(", ", maxsplit=1) for line in file.readlines() if line.strip()
        ]
        # Create a dictionary mapping task IDs to industries
        task_industry_map = {int(task_id): industry for task_id, industry in task_industry_pairs}
except FileNotFoundError:
    print(f"Error: File not found at {file_path_new_task_ids}")
    task_industry_map = {}


current_matched_task_ids_in_a_list = [
    id_ for id_ in task_industry_map.keys() if id_ in lst_of_all_tsk_ids
]

print(f"We Gathered {len(lst_of_all_tsk_ids)} Tasks, moving to parse.")


for task_id_iter in current_matched_task_ids_in_a_list:

    try:
        data = {
            "id": 1 ,
            "method": "tasks.getTaskResult",
            "params": {
                "taskId": task_id_iter
            }
        }
        resp_for_json_serp_data = requests.post(api_url, json=data, headers=headers)
        json_serp_data = resp_for_json_serp_data.json()
        lst_of_keyword_data.append((task_id_iter, json_serp_data))

    except Exception as e:
        print(e)
        break

print("Gathered all the data now creating dataframe")

full_df_data = []

for task_id, item in lst_of_keyword_data:
    print(task_id)
    try:
        region_id = item['result']['task_meta']['region_id']
        result = item['result']['tops']

        for entry in result:

            keyword_id = entry['keyword_id']
            keyword_data = entry['keyword_data']['top']

            for seq_data in keyword_data:

                url = seq_data['url']
                domain = seq_data['domain']
                subdomain = seq_data['subdomain']
                title = seq_data['title']
                title_len = seq_data['title_length']
                snippet = seq_data['snippet']
                spec_elements = seq_data['spec_elements']
                snippet_len = seq_data['snippet_length']
                breadcrumbs = seq_data['breadcrumbs']
                types = seq_data['types']
                position = seq_data['position']

                full_df_data.append((task_id,region_id, keyword_id, position, url, domain, subdomain, title, title_len, snippet, snippet_len, spec_elements, breadcrumbs, types ))
    except Exception as e:
        print(e)
        continue


serp_data_df = pd.DataFrame(full_df_data, columns=['task_id', 
                                            'region_id', 
                                            'keyword_id', 
                                            'position' , 
                                            'url', 
                                            'domain', 
                                            'subdomain' , 
                                            'title', 'title_length', 
                                            'snippet', 'snippet_length', 'spec_elements', 
                                            'breadcrumbs','types'])

serp_data_df['keyword_id'] = serp_data_df['keyword_id'].astype(int)
serp_data_df['region_id'] = serp_data_df['region_id'].astype(int)
serp_data_df['keyword_id'] = serp_data_df['keyword_id'].astype(int)


print("Finishing up the dataframe with final joins.")

keyword_data = []
keywords_and_seo_data = []

for task, item in lst_of_keyword_data:
    data = item['result']['tops']
    keyword_data.extend(data)

for ky_data in keyword_data:
    keywords_and_seo_data.append((ky_data['keyword_id'], ky_data['keyword'], ky_data['keyword_data']))

df_of_keywords = pd.DataFrame(keywords_and_seo_data, columns=['Keyword ID', 'Keyword', 'Keyword Data'])
df_keyword_content_id = df_of_keywords[['Keyword ID', 'Keyword']].copy()
df_additional_data = df_of_keywords.drop(columns=['Keyword'])
df_keyword_content_id.rename(columns={'Keyword ID' : 'keyword_id', 'Keyword' : 'keyword'}, inplace=True)
df_keyword_content_id['keyword_id'] = df_keyword_content_id['keyword_id'].astype(int)

df_merged_keywords = pd.merge(serp_data_df, df_keyword_content_id, on="keyword_id", how="left")
df_merged_location = pd.merge(df_merged_keywords,locations_full_df, on='region_id', how="left")

# Add the industry column based on the task_i

df_merged_final = df_merged_location[["task_id", "region_id", "keyword_id", "region_state","region_name", "keyword", "position", "url", 
"domain", "subdomain", "title", "title_length", "snippet", "snippet_length", "spec_elements", "breadcrumbs", "types"]]

df_merged_final['industry'] = df_merged_final['task_id'].map(task_industry_map)


print("Serp Crawl Finished")
output_path = os.path.join(base_path, "raw_serp_data.csv")

# output_path = "C:/Users/nickj/OneDrive/Desktop/Xoinx/Code/GUI/raw_serp_data.csv"
df_merged_final.to_csv(output_path, index=False)
