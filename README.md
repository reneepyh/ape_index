# Ape Index - BAYC NFT Analytics

Ape Index is a **data engineering project** that provides analytics on the **Bored Ape Yacht Club (BAYC) NFT marketplace**. It processes and analyzes **transaction data from Etherscan** to deliver insights into **historical sales, top buyers/sellers, marketplace comparisons, and top resale tokens**.

The project consists of **two data pipelines**:
- **API Service Pipeline**: Provides NFT analytics via a **FastAPI REST API**.
- **Data Warehouse Pipeline**: Uses **Spark (EMR) and Redshift** to power **Tableau dashboards**.

**Website**: [Ape Index - BAYC NFT 分析儀表板](<https://ape-index-nft.com/>)  
[**Tableau Dashboard**](<https://ape-index-nft.com/](https://public.tableau.com/app/profile/renee.hsu1430/viz/shared/48GB7T75P>)

---

## Table of Contents
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Job API](#api)
- [Visualization](#visualization)
- [Technologies Used](#technologies-used)
- [Contact](#contact)

---

## Architecture

Ape Index is structured into two main pipelines that handle **real-time NFT analytics and data warehousing**.

### **1. API Service Pipeline (FastAPI & MySQL)**
- Runs on **AWS ECS (Fargate)** to provide **NFT analytics via REST API**.
- Uses **AWS RDS (MySQL)** to store **processed transaction data**.
- Allows frontend and external applications to fetch **NFT statistics**.

### **2. Data Warehouse Pipeline (Spark & Redshift)**
- Runs on **AWS EMR (Spark)** to handle **ETL processing**.
- Stores NFT sales data in **Amazon Redshift** for business intelligence.
- **Tableau BI Dashboard** connects to Redshift for **visual analytics**.

### **Orchestration**
- **Airflow DAG (AWS EC2)** manages both pipelines.
- **AWS Fargate** executes **Pandas-based ETL** for the API service.
- **AWS EMR (Spark)** processes large-scale transactions for **Redshift**.

---

## Data Pipeline

### **1. API Pipeline (FastAPI & MySQL)**
#### **Extract**
- **Playwright Web Scraper** fetches NFT transactions from **Etherscan**.
- Uses a **proxy service to avoid scraper detection when crawling in ECS Fargate**.
- Raw data is **stored in AWS S3**.

#### **Transform**
- **Pandas ETL**
  - Cleans and processes raw transaction data by **removing duplicates, filtering out invalid entries, and extract USD value as a string**.
  - Normalizes **buyers, sellers, and marketplaces** into separate relational tables.

#### **Load**
- **AWS RDS (MySQL)** stores **processed transaction data**.
- **FastAPI** provides an API to access **NFT analytics**.

---

### **2. Data Warehouse Pipeline (Spark & Redshift)**
#### **Extract**
- Reads **raw transaction data from AWS S3**.

#### **Transform**
- **Spark (AWS EMR)**
  - Computes **seller addresses** by applying a **window function (lag)** on transactions grouped by `token_id`, ensuring that each sale is linked to its previous buyer.
  - **Maps transactions to Redshift dimension tables** for efficient querying.

#### **Load**
- Stores structured data in **Amazon Redshift**.
- **Tableau BI Dashboard** connects to Redshift for insights.

---

## API

#### **Protocol & Host**
- **Protocol:** HTTPS  
- **Host Name:** `https://ape-index-nft.com/`  
- **Method:** `GET`

#### **API Endpoints**
| Endpoint                                  | Purpose                                                                                                           |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `/api/v1/time-based-data`                 | Retrieve aggregated sales volume, average price, and highest sale over different time intervals.                  |
| `/api/v1/top-buyers-sellers`              | Identify the top 5 buyers and sellers based on transaction volume.                                                |
| `/api/v1/marketplace-comparison`          | Compare NFT sales across different marketplaces.                                                                  |
| `/api/v1/top-resale-token`                | Fetch the top 5 NFT resales with the highest profit margin.                                                       |
| `/api/v1/token-transaction?token_id={id}` | Get historical transactions for a specific NFT token.                                                             |
| `/api/v1/nft-details?token_id={id}`       | Fetch metadata (image, rarity, attributes) for a specific NFT by calling a third-party API.                   |

---

## Visualization
- **Website Dashboard (HTML, JS, Plotly.js)** visualizes **NFT transaction insights**.
- **Tableau** connects to **Redshift** for BI dashboards.

---

## Technologies Used
- **Backend**: FastAPI, SQLAlchemy
- **Web Scraping**: Playwright
- **ETL (API Pipeline)**: Pandas, AWS ECS (Fargate), MySQL (RDS)
- **ETL (Data Warehouse Pipeline)**: Apache Spark, AWS EMR, Amazon Redshift
- **Orchestration**: Apache Airflow
- **Storage**: AWS S3
- **BI & Visualization**: Tableau, HTML, JS, Plotly.js
- **Infrastructure**: AWS EC2, AWS ECS (Fargate), AWS Route 53, Nginx

---

## Contact

