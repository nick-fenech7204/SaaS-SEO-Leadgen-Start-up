SELECT *
FROM search_engine_result_data
JOIN region_data ON search_engine_result_data.region_data_id = region_data.region_data_id;



-- Need to use concurrecy for site audit sending, cannot scale with Async, look to .py files to fix, need for Prosites  