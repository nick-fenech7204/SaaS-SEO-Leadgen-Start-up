GO
-- Drop cols and make connection DML after injection
use SerpStat;

GO 

UPDATE search_engine_result_data
SET 
    region_data_id = (SELECT region_data_id FROM region_data WHERE region_id = search_engine_result_data.region_id),
    all_keyword_data_id = (SELECT all_keyword_data_id FROM all_keyword_data WHERE keyword_id = search_engine_result_data.keyword_id),
    task_meta_data_id = (SELECT task_meta_data_id FROM task_meta_data WHERE task_id = search_engine_result_data.task_id);
GO

UPDATE full_details_site_health
SET meta_data_site_health_id = m.meta_data_site_health_id
FROM full_details_site_health f
JOIN meta_data_site_health m ON f.reportId = m.reportId;



UPDATE keyword_metric_full_data
SET keyword_metric_full_data.keyword_metric_meta_data_id = keyword_metric_meta_data.keyword_metric_meta_data_id
FROM keyword_metric_full_data
JOIN keyword_metric_meta_data ON keyword_metric_full_data.task_id = keyword_metric_meta_data.task_id;

GO

ALTER TABLE full_details_site_health
DROP COLUMN reportId;

GO 

ALTER TABLE keyword_metric_full_data
DROP COLUMN task_id;

GO 

ALTER TABLE search_engine_result_data
DROP COLUMN region_id;

GO 

ALTER TABLE search_engine_result_data
DROP COLUMN task_id;

GO

ALTER TABLE search_engine_result_data
DROP COLUMN keyword_id;

GO

ALTER TABLE data_main_error
DROP COLUMN main_error_key;

GO

ALTER TABLE data_priority_error
DROP COLUMN priority_error_key;

GO

ALTER TABLE data_sub_error
DROP COLUMN sub_error_key;