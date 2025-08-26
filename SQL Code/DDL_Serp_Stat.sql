use master;
GO
drop database if exists SerpStat;
GO
create database SerpStat;
GO
use SerpStat;
GO

--- HL build the backlinks ones, and build the final site health one, once thats done start researching the cloud, all HL points

drop table if EXISTS [search_engine_result_data]
drop table if EXISTS [region_data]
drop table if EXISTS [all_keyword_data]
drop table if EXISTS [task_meta_data]

create TABLE [task_meta_data](
    task_meta_data_id INT PRIMARY KEY IDENTITY (1,1),
    task_id INT,
    client_name NVARCHAR(MAX), 
    se_id SMALLINT,
    country_id INTEGER,
    lang_id SMALLINT,
    device_type_id SMALLINT,
    progress NVARCHAR(MAX), 
    keywords_count NVARCHAR(MAX), 
    created_at DATETIME,
    parsed_at DATETIME
);


CREATE TABLE [region_data] (
    region_data_id INT PRIMARY KEY IDENTITY (1,1),
    region_id INT,
    zipcode NVARCHAR(20), 
    location_name NVARCHAR(255), 
    parent_id NVARCHAR(50), 
    country_code NVARCHAR(10), 
    target_type NVARCHAR(50) 
);


CREATE TABLE [all_keyword_data] (
    all_keyword_data_id INT PRIMARY KEY IDENTITY (1,1),
    keyword_id INT,
    keyword NVARCHAR(MAX)
);


CREATE TABLE [search_engine_result_data] (
    search_engine_result_data_id INT PRIMARY KEY IDENTITY(1,1),
    region_data_id INT,
    all_keyword_data_id INT,
    task_meta_data_id INT,
    region_id INT,
    task_id INT,
    keyword_id INT,
    position SMALLINT,
    [url] NVARCHAR(MAX),
    domain NVARCHAR(MAX),
    subdomain NVARCHAR(MAX),
    title NVARCHAR(MAX),
    title_length SMALLINT,
    snippet NVARCHAR(MAX),
    snippet_length SMALLINT,
    spec_elements NVARCHAR(MAX), -- JSON Data
    breadcrumbs NVARCHAR(MAX),
    types NVARCHAR(MAX), -- JSON Data
    CONSTRAINT FK_region_data_id FOREIGN KEY (region_data_id) REFERENCES region_data(region_data_id),
    CONSTRAINT FK_task_meta_data_id FOREIGN KEY (task_meta_data_id) REFERENCES task_meta_data(task_meta_data_id),
    CONSTRAINT FK_all_keyword_data_id FOREIGN KEY (all_keyword_data_id) REFERENCES all_keyword_data(all_keyword_data_id)
);



-- Drop columns from search_engine_result_data table
-- ALTER TABLE search_engine_result_data
-- DROP COLUMN region_id,
-- DROP COLUMN task_id,
-- DROP COLUMN keyword_id;


-- Above tables are used for SERP Crawling API

drop table if EXISTS [domain_data_for_backlinks]

CREATE TABLE [domain_data_for_backlinks] (

    domain_data_for_backlinks_id INT PRIMARY KEY IDENTITY (1,1),
    client_name NVARCHAR(MAX), 
    domain NVARCHAR(MAX),
    request_datetime DATETIME,
    sersptat_domain_rank SMALLINT,
    referring_domains INTEGER,
    referring_domains_change INTEGER,
    redirected_domains INTEGER,
    referring_malicious_domains INTEGER,
    referring_malicious_domains_change INTEGER,
    referring_ip_addresses INTEGER,
    referring_ip_addresses_change INTEGER,
    referring_subnets INTEGER,
    referring_subnets_change INTEGER,
    backlinks INTEGER,
    backlinks_change INTEGER,
    backlinks_from_mainpages INTEGER,
    backlinks_from_mainpages_change INTEGER,
    nofollow_backlinks INTEGER,
    nofollow_backlinks_change INTEGER,
    dofollow_backlinks INTEGER,
    dofollow_backlinks_change INTEGER,
    text_backlinks INTEGER,
    text_backlinks_change INTEGER,
    image_backlinks INTEGER,
    image_backlinks_change INTEGER,
    redirect_backlinks INTEGER,
    redirect_backlinks_change INTEGER,
    canonical_backlinks INTEGER,
    canonical_backlinks_change INTEGER,
    alternate_backlinks INTEGER,
    alternate_backlinks_change INTEGER,
    rss_backlinks INTEGER,
    rss_backlinks_change INTEGER,
    frame_backlinks INTEGER,
    frame_backlinks_change INTEGER,
    form_backlinks INTEGER,
    form_backlinks_change INTEGER,
    external_domains INTEGER,
    external_domains_change INTEGER,
    external_malicious_domains INTEGER,
    external_malicious_domains_change INTEGER,
    external_links INTEGER,
    external_links_change INTEGER
);

-- Above table is used for BackLinks API
-- need to change ID to be int
drop table if EXISTS [full_details_site_health]
drop table if EXISTS [meta_data_site_health]
drop table if EXISTS [data_sub_error]
drop table if EXISTS [data_main_error]
drop table if EXISTS [data_priority_error]


CREATE TABLE [meta_data_site_health] (
    meta_data_site_health_id INT PRIMARY KEY IDENTITY (1,1),
    reportId INT,
    domain NVARCHAR(MAX),
    [date] DATETIME,
    sdo SMALLINT,
    highCount SMALLINT,
    mediumCount SMALLINT,
    lowCount SMALLINT,
    informationCount SMALLINT,
    virusesCount SMALLINT,
    progress SMALLINT,
    [stoped] SMALLINT,
    specialStopReason SMALLINT,
    checkedPageCount SMALLINT,
    totalCheckedPageCount SMALLINT,
    redirectCount SMALLINT,
    captchaDetected BIT,
    hasDetailData BIT
);

CREATE TABLE [data_sub_error] (
    data_sub_error_id INT PRIMARY KEY IDENTITY (1,1),
    sub_error_key INT,
    sub_error NVARCHAR(MAX)
);


CREATE TABLE [data_priority_error] (
    data_priority_error_id INT PRIMARY KEY IDENTITY (1,1),
    priority_error_key INT, 
    [priority] NVARCHAR(MAX)
);


CREATE TABLE [data_main_error] (
    data_main_error_id INT PRIMARY KEY IDENTITY (1,1),
    main_error_key INT,
    main_error NVARCHAR(MAX)
)

CREATE TABLE [full_details_site_health] (
    site_audit_full_details_id INT PRIMARY KEY IDENTITY (1,1),
    data_main_error_id INT,
    data_sub_error_id INT,
    data_priority_error_id INT,
    meta_data_site_health_id INT,
    count_of_all_errors INTEGER,
    count_of_new_errors INTEGER,
    count_of_fixed_errors INTEGER,
    reportId INT,
    CONSTRAINT FK_data_sub_error_id FOREIGN KEY (data_sub_error_id) REFERENCES data_sub_error(data_sub_error_id),
    CONSTRAINT FK_data_priority_error_id FOREIGN KEY (data_priority_error_id) REFERENCES data_priority_error(data_priority_error_id),
    CONSTRAINT FK_data_main_error_id FOREIGN KEY (data_main_error_id) REFERENCES data_main_error(data_main_error_id),
    CONSTRAINT FK_meta_data_site_health_id FOREIGN KEY (meta_data_site_health_id) REFERENCES meta_data_site_health(meta_data_site_health_id)
);

-- Above table is used for Site Health API

drop table if EXISTS [keyword_metric_meta_data]
drop table if EXISTS [keyword_metric_full_data]


CREATE TABLE [keyword_metric_meta_data] (
    keyword_metric_meta_data_id INT PRIMARY KEY IDENTITY (1,1),
    task_id NVARCHAR(MAX),
    total INT, 
    type_id NVARCHAR(MAX),
    se_id NVARCHAR(MAX),
    region_id NVARCHAR(MAX),
    [match] NVARCHAR(MAX)
)

CREATE TABLE [keyword_metric_full_data] (
    keyword_metric_full_data_id INT PRIMARY KEY IDENTITY (1,1),
    keyword_metric_meta_data_id INT,
    task_id NVARCHAR(MAX),
    keyword NVARCHAR(MAX),
    keyword_raw NVARCHAR(MAX),
    [status] INTEGER,
    cost FLOAT(4), 
    search_volume INTEGER,
    competition INTEGER,
    search_volume_history NVARCHAR(MAX) -- Chnage to json or string the data
    
    CONSTRAINT FK_keyword_metric_meta_data_id FOREIGN KEY (keyword_metric_meta_data_id) REFERENCES keyword_metric_meta_data(keyword_metric_meta_data_id),
);

