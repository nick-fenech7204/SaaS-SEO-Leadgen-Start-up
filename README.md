# SEO Lead Generation & Enrichment Tool

## Overview

This application automates SEO lead generation and enrichment by combining **Serpstat** (for unbiased SERP crawling & keyword intelligence) with **Wiza** (for enriched contact data).

The goal is simple:  
Help SEO firms and digital marketing agencies find high-potential prospects—websites that are actively competing in search results but underperforming enough to need SEO services.

By crawling local SERPs by keyword, industry, and location, filtering results intelligently, and then enriching domains with real business contact information, the tool produces sales-ready leads in minutes.

---

## Key Features

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

### Contact Enrichment (via Wiza API)
- Fetches company contacts from each domain.  
- Provides **name, title, LinkedIn, email, phone, and firmographics**.  

### Sales-Ready Output
- Produces structured lead lists that SEO agencies can immediately use for outreach.  

---

## How It Works

1. **Input Parameters**  
   - Location (city/state/DMA/zip)  
   - Industry category (Serpstat taxonomy)  
   - Keywords or search phrases  

2. **SERP Crawl (Serpstat)**  
   - Executes unbiased searches in the chosen region.  
   - Collects the top 100 organic results per keyword.  

3. **Filtering & Lead Scoring**  
   - Keep only results ranked **6–30**.  
   - Check traffic volume (exclude large enterprises).  
   - Match against the specified industry.  

4. **Enrichment (Wiza)**  
   - For each domain, pull contact and company data.  
   - Collects decision-maker info (CMOs, Marketing Managers, Founders, etc.).  

5. **Output**  
   - A clean, enriched lead list with domains, traffic metrics, and contacts.  

---

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
- (Optional) Virtual environment for clean setup  

### Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
### Install Dependencies
```bash
pip install -r requirements.txt
```



