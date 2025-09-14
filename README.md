# Snowflake Data Quality Manager - Working Version

Working version of the Data Quality Manager Streamlit app from Snowflake Solutions Innovation Team.

## Installation

1. Run `install.sql` in your Snowflake account
2. Upload files to Snowflake stage (see commands below)
3. Configure database list in `streamlit_app.py` line 21
4. Access app in Snowflake under Streamlit Apps

## Configuration Required

### 1. Update Warehouse Name (if needed)
**File:** `install.sql` line 284
```sql
-- Change this line if you don't have COMPUTE_WH
QUERY_WAREHOUSE = COMPUTE_WH
```

### 2. Configure Databases to Monitor  
**File:** `streamlit_app.py` line 21
```python
# Replace with your actual database names
st.session_state.databases = ["DATA_QUALITY"]
```

### 3. Environment Dependencies
**File:** `environment.yml` - already includes required packages:
- pandas
- snowflake-snowpark-python  
- snowflake-ml-python
- matplotlib=3.7.2

### 4. Connection Handler
**File:** `snowflake_conn.py` - handles Snowflake session connections

## File Upload Commands

After running `install.sql`, upload files with these commands:

```sql
USE DATABASE DATA_QUALITY;
USE SCHEMA CONFIG;

PUT file://streamlit_app.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://snowflake_conn.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://utility_functions.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://utility_functions_non_stat.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://environment.yml @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://src/* @DATA_QUALITY.CONFIG.CODE/src/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/* @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/* @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

## What This App Does

- Monitor data quality using Snowflake DMFs
- Create anomaly detection checks
- Schedule quality checks as Snowflake tasks
- View alerts and quality metrics
- Generate quality reports

## Original Source

Based on: https://github.com/Snowflake-Labs/emerging-solutions-toolbox/tree/main/sfguide-getting-started-with-data-quality-manager