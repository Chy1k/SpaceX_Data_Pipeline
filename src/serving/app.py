import streamlit as st
import duckdb
import pandas as pd
import os
import json

# --- 1. Configuration & Connection ---
st.set_page_config(page_title="SpaceX Rocket Reliability Dashboard", layout="wide")

# Cache the connection so Streamlit doesn't reconnect on every interaction
@st.cache_resource
def get_db_connection():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    gold_db_path = os.path.join(current_script_dir, "..", "..", "data", "gold", "spacex_data.duckdb")
    return duckdb.connect(gold_db_path)

conn = get_db_connection()

# --- 2. Data Retrieval ---
@st.cache_data
def get_failure_data():
    query = "SELECT * FROM agg_rocket_failure_analysis ORDER BY failure_rate_pct DESC"
    return conn.execute(query).fetchdf()

df = get_failure_data()

# --- 3. Dashboard UI ---
st.title("🚀 SpaceX Rocket Reliability Dashboard")
st.markdown("Analyzing which rockets experience the most launch failures.")

# Create columns for high-level metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Rockets Analyzed", len(df))
with col2:
    highest_failure_rate = f"{df['failure_rate_pct'].max()}%"
    st.metric("Highest Failure Rate", highest_failure_rate)

# Create a bar chart
st.subheader("Failure Rates by Rocket ID")
st.bar_chart(data=df, x='rocket_id', y='failure_rate_pct')

# Create a data table
st.subheader("Detailed Aggregated Data")
st.dataframe(df, use_container_width=True)

# --- 4. Text Analysis Insights ---
st.subheader("🔍 Anomaly Log Analysis")

@st.cache_data
def get_anomaly_log():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    silver_dir = os.path.join(current_script_dir, "..", "..", "data", "silver", "weather_logs")
    log_file = os.path.join(silver_dir, "anomaly_report.json")
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            # Read the file, handling potential JSONL (multiple JSON objects)
            lines = f.readlines()
            data = [json.loads(line) for line in lines if line.strip()]
        return pd.DataFrame(data)
    return pd.DataFrame()

log_df = get_anomaly_log()

if not log_df.empty:
    st.info(f"Found {len(log_df)} anomaly reports.")
    
    # Metric: Total Issues Found by AI
    total_issues = int(log_df['issue_count'].sum())
    st.metric("Total Issues Identified by AI", total_issues)
    
    # Most Common Issues
    top_issues = log_df['issue_type'].value_counts().head(5)
    st.subheader("Top 5 Most Common Issues:")
    st.bar_chart(top_issues)
    
    # Sample Log Entries
    st.subheader("Sample Log Entries:")
    for _, row in log_df.head(3).iterrows():
        with st.expander(f"{row['ingestion_date']} - {row['issue_type']} ({row['issue_count']} instances)", expanded=False):
            st.code(f"Summary: {row['summary']}")
            st.write(f"Location: {row['location']}")
            st.write(f"Severity: {row['severity_level']}")
else:
    st.success("No anomaly logs found. Run the pipeline to generate insights!")