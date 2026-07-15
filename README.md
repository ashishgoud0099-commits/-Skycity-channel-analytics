# SkyCity Auckland Restaurants & Bars — Order Channel Performance Analytics

Business analytics project analyzing order channel performance and market share 
across 1,696 restaurants in Auckland, New Zealand, covering In-Store, Uber Eats, 
DoorDash, and Self-Delivery channels.

## Live Dashboard
[View the deployed Streamlit app](https://v22jghswbbsmbuxhbpauxt.streamlit.app/)

## What this project covers
- Data validation and consistency checks (including identifying and correcting 
  an anomaly in the dataset's provided share columns)
- Channel volume aggregation by subregion, cuisine type, and business segment
- Geographic and cuisine-based channel preference analysis
- Channel dependency risk identification (70%+ single-aggregator threshold)
- 5 core KPIs: Channel Order Share, Aggregator Dependence Index, In-Store 
  Reliance Ratio, Channel Diversification Score, and Subregion Channel Dominance

## Key findings
- Uber Eats holds ~40% market share overall, and dominates almost identically 
  (~39.6–39.7%) across every Auckland subregion
- Pizza restaurants show the lowest aggregator dependence (26.7% Uber Eats share) 
  of any cuisine; Kebabs/Mediterranean and Japanese show the highest (48% each)
- Ghost Kitchens operate almost entirely on delivery channels (94% of orders)
- No restaurant crosses the 70% single-aggregator dependency threshold, but 
  ~32% of restaurants show negative profitability on Uber Eats and DoorDash orders

## Files in this repo
- `app.py` — Streamlit dashboard source code
- `SkyCity_Auckland_Restaurants___Bars.csv` — dataset used by the dashboard
- `SkyCity Auckland Restaurants & Bars.xlsx` — Excel workbook with validation, 
  pivot tables, and KPI calculations
- `requirements.txt` — Python dependencies for deployment

## How to run locally
