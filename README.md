# Ape Index - BAYC NFT Analytics

Ape Index is a data engineering project that provides analytics on the **Bored Ape Yacht Club (BAYC) NFT** marketplace. The project fetches, processes, and analyzes transaction data, allowing users to gain insights into **historical sales, top buyers/sellers, marketplace comparisons, and top resale tokens**.

## Features

- **Time-Based Analytics**: Aggregate sales volume, average price, and highest-priced NFT over different time intervals.
- **Top Buyers & Sellers**: Identify the most active buyers and sellers by transaction volume.
- **Marketplace Comparison**: Compare NFT sales performance across various marketplaces.
- **Top Resale Tokens**: Track the most profitable NFT resales.
- **Token Transaction History**: Fetch historical transactions for a specific NFT.
- **NFT Metadata Fetching**: Retrieve metadata (image, rarity) for an NFT.

## Architecture Overview

Ape Index consists of two main components:

### **Backend Service** (`FastAPI` & `ETL Pipeline`)
- Provides REST API endpoints for NFT analytics.
- Processes transaction data using an ETL pipeline.
- Stores data in **AWS RDS (MySQL)**.

### **Frontend Service** (`HTML, JS, Plotly.js`)
- A web dashboard visualizing BAYC NFT transaction insights.
- Fetches data from the backend API.
- Uses **Plotly.js** for interactive charts.

## Data Engineering Pipeline

The project follows a **traditional ETL (Extract, Transform, Load) pipeline**, orchestrated using **Apache Airflow**.

### **Data Extraction**
- Uses `Playwright` for web scraping to extracts NFT transaction data and marketplace data.
- Stores raw data in **AWS S3**.

### **Data Transformation**
- Cleans and processes data using **Pandas**.
- Prepares normalized tables for buyers, sellers, and marketplaces.

### **Data Loading**
- Inserts cleaned data into an **AWS RDS MySQL database**.

### **Orchestration**
- **AWS ECS (Fargate)** triggers the ETL pipeline at scheduled intervals.
- **Airflow DAG** manages the extraction, transformation, and loading process.
