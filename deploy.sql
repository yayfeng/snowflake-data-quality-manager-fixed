-- Data Quality Manager Deployment Script
-- This script helps you deploy the Data Quality Manager to your Snowflake account
-- 
-- IMPORTANT: Please update the warehouse name below before running
-- Replace 'COMPUTE_WH' with your actual warehouse name

-- Step 1: Set your warehouse name
SET WAREHOUSE_NAME = 'COMPUTE_WH';  -- UPDATE THIS LINE

-- Step 2: Create the database and objects (run install.sql first)
-- Make sure you have already run install.sql

-- Step 3: Use the correct database and schema
USE DATABASE DATA_QUALITY;
USE SCHEMA CONFIG;

-- Step 4: Upload files to stage
-- Run these commands from your local directory where the files are located:

/*
PUT file://streamlit_app.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://src/* @DATA_QUALITY.CONFIG.CODE/src/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://utility_functions.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://utility_functions_non_stat.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://snowflake_conn.py @DATA_QUALITY.CONFIG.CODE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/* @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/* @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
*/

-- Step 5: Update the Streamlit app with the correct warehouse
CREATE OR REPLACE STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER
ROOT_LOCATION = '@DATA_QUALITY.CONFIG.CODE'
MAIN_FILE = '/streamlit_app.py'
QUERY_WAREHOUSE = IDENTIFIER($WAREHOUSE_NAME)
COMMENT = '{"origin": "sf_sit","name": "sit_data_quality_framework","version": "{major: 2, minor: 0}"}';

-- Step 6: Grant permissions (adjust as needed for your security model)
GRANT USAGE ON DATABASE DATA_QUALITY TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA DATA_QUALITY.CONFIG TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA DATA_QUALITY.RESULTS TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA DATA_QUALITY.TEMPORARY_DQ_OBJECTS TO ROLE PUBLIC;
GRANT USAGE ON STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER TO ROLE PUBLIC;

-- Step 7: Verify deployment
SELECT 'Deployment completed successfully. You can now access the Data Quality Manager Streamlit app.' AS status;
SHOW STREAMLITS IN SCHEMA DATA_QUALITY.CONFIG;
