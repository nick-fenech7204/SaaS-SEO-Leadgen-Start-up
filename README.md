# SEO Lead Generation & Enrichment Tool

## Overview:

This application automates SEO lead generation and enrichment by combining:

- **[SerpStat](https://serpstat.com)** - for unbiased SERP crawling & keyword/industry intelligence  
- **[Wiza](https://wiza.co)** - for enriched contact data  
- **[OpenAI](https://openai.com)** - for dynamic keyword generation, industry insights, and guidance 

The goal is simple:

Help SEO firms and digital marketing agencies find high-potential prospects—websites that are actively competing in search results but underperforming enough to need SEO services.
By crawling local SERPs by keyword, industry, and location, filtering results intelligently, and then enriching domains with real business contact information, the tool produces sales-ready leads in minutes.

---

## Key Aspects:

### Localized SERP Crawling
- Uses Serpstat’s Local SERP API to simulate unbiased Google Chrome searches.  
- Supports city, state, DMA, and zip code targeting.  
- Pulls the top 100 organic results per keyword.  

### Lead Qualification & Filtering
- Filters results to focus on positions **6–30** (beyond page one, but still competitive).  
- Excludes large firms with very high traffic.  
- Validates industry category against Serpstat’s taxonomy.  

### SEO-Focused Targeting
- Ensures leads match the **keywords + industry** you’re prospecting.  
- Prioritizes businesses that could benefit most from SEO improvements.
  
### AI-Powered Keyword Generation (via OpenAI API)
- Suggests keyword ideas for a given industry or niche.  
- Helps discover **long-tail phrases** and underserved opportunities.  
- Can be queried interactively for strategy support.
  
### Contact Enrichment (via Wiza API)
- Fetches company contacts from each domain.  
- Provides **name, title, LinkedIn, email, phone, and firmographics**.  

### Sales-Ready Output
- Produces structured lead lists that SEO agencies can immediately use for outreach.  

---

## App Flow:

1. **Input Parameters**  
   - Location (city/state/DMA/zip)  
   - Industry category (Serpstat taxonomy)  
   - Keywords or search phrases (or ask OpenAI to generate them)  

2. **Keyword Assistance (OpenAI)**  
   - If no keywords are provided by the firm, the tool can call the OpenAI API for assistance.  
   - Returns relevant, industry-specific keyword lists.
   - Can be used for any other needs within the app.

3. **SERP Crawl (Serpstat)**  
   - Executes unbiased searches in the chosen region.  
   - Collects the top 100 organic results per keyword.  

4. **Filtering & Lead Scoring**  
   - Keep only results ranked **6–30**.  
   - Check traffic volume, keyword count, and ads (exclude large enterprises and those assumed to already be receiving services).
   - Match against the specified industry.  

5. **Enrichment (Wiza)**  
   - For each domain, pull contact and company data.  
   - Collects decision-maker info (CMOs, Marketing Managers, Founders, etc.).  

6. **Output (Excel file with three sheets)**  
   - Raw Data: Contains the raw SERP Crawled Data
   - Domains: Lists all domains that fit filtering criteria
   - Wiza: All leads and their contact information from the above domains
   - [Output Example](Examples%20and%20Required%20Docs/example_serp_crawl_output.xlsx)

---
## App Example:
![SerpCrawling App](Serp%20Crawler%20-%20Lead%20Generator/example_program.png)


## Example Use Case

- An SEO agency in Florida wants new clients in the healthcare industry.  
- The tool crawls local searches for terms like *“family doctor Orlando”*, *“urgent care Jacksonville”*, etc.  
- It identifies practices ranking on page 2 or 3.  
- Large healthcare networks are excluded, leaving independent practices.  
- Wiza enriches the domains with contact info → The agency has a **direct outreach list of qualified prospects**.  

---

## Installation & Setup

### Prerequisites
- Python 3.9+  
- Serpstat API key  
- Wiza API key
- OpenAI API Key
  
### Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Run App
```bash
serp_crawling_app.py 
```

## Offshoot Capabilities of This Solution

### Database Integration (SQL)

A **CRM Integration - Database Example** was used to simulate the integration of Serpstat data into an existing firm's CRM.  

Note: This differs from the main **SerpCrawler** script app.  
While the crawler is focused on generating *new SEO leads*, this database showcases how enrichment data can be layered onto **existing leads** already within a firm's CRM.  

The database contains:  
- **Backlink information**  
- **Site audit data** (site health, technical issues)  
- **SERP performance metrics**  

This enriched dataset can be valuable not only for SEO firms, but also for **marketing agencies** and **in-house marketing departments** across many industries.  
This is not the primary focus of this repo, however it demonstrates the **potential for CRM enrichment and cross-departmental insights**.  

### API Notebooks

The **SerpStat API Calls** folder contains Jupyter notebooks with information and examples on calling almost all API methods within SerpStat's documentation:
This is helpful in understanding what data is accessible with a subscription, and how to send the post requests correctly for the many different methods. 

### Disclaimer
This solution is provided as an example of a business use case for SEO lead generation and enrichment. This repository can be used as a reference or starting point for similar applications in digital marketing and SEO outreach or even a jumping off point for a future SaaS soultion.




