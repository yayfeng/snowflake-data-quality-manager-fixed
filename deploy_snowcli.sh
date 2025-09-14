#!/bin/bash

# Data Quality Manager Deployment Script using SnowCLI
# This script deploys the Data Quality Manager to your Snowflake account

set -e  # Exit on any error

echo "🚀 Starting Data Quality Manager deployment with SnowCLI..."

# Check if SnowCLI is installed
if ! command -v snow &> /dev/null; then
    echo "❌ SnowCLI is not installed. Please install it first:"
    echo "pip install snowflake-cli-labs"
    exit 1
fi

# Check if snowflake.yml exists
if [ ! -f "snowflake.yml" ]; then
    echo "❌ snowflake.yml not found. Please make sure you're in the correct directory."
    exit 1
fi

# Step 1: Configure connection (if not already done)
echo "📋 Step 1: Configure your Snowflake connection"
echo "Please run: snow connection add --connection-name default"
echo "Or update the connection details in snowflake.yml"
read -p "Press Enter to continue once your connection is configured..."

# Step 2: Create database and schema objects
echo "📋 Step 2: Creating database objects..."
snow sql -q "$(cat install.sql)" --connection default

# Step 3: Create stage and upload files
echo "📋 Step 3: Creating stage and uploading files..."
snow object stage create DATA_QUALITY.CONFIG.CODE --connection default

# Upload Python files
echo "📤 Uploading application files..."
snow object stage put streamlit_app.py @DATA_QUALITY.CONFIG.CODE --connection default --overwrite
snow object stage put snowflake_conn.py @DATA_QUALITY.CONFIG.CODE --connection default --overwrite
snow object stage put utility_functions.py @DATA_QUALITY.CONFIG.CODE --connection default --overwrite
snow object stage put utility_functions_non_stat.py @DATA_QUALITY.CONFIG.CODE --connection default --overwrite

# Upload src directory
echo "📤 Uploading src directory..."
for file in src/*.py; do
    if [ -f "$file" ]; then
        snow object stage put "$file" @DATA_QUALITY.CONFIG.CODE/src/ --connection default --overwrite
    fi
done

# Upload stored procedure packages
echo "📤 Uploading stored procedure packages..."
if [ -d "DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374" ]; then
    for file in DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/*; do
        if [ -f "$file" ]; then
            snow object stage put "$file" @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374/ --connection default --overwrite
        fi
    done
fi

if [ -d "DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498" ]; then
    for file in DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/*; do
        if [ -f "$file" ]; then
            snow object stage put "$file" @DATA_QUALITY.CONFIG.CODE/DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498/ --connection default --overwrite
        fi
    done
fi

# Step 4: Deploy Streamlit app
echo "📋 Step 4: Deploying Streamlit application..."
snow streamlit deploy --connection default

# Step 5: Grant permissions
echo "📋 Step 5: Setting up permissions..."
snow sql -q "GRANT USAGE ON DATABASE DATA_QUALITY TO ROLE PUBLIC;" --connection default
snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.CONFIG TO ROLE PUBLIC;" --connection default
snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.RESULTS TO ROLE PUBLIC;" --connection default
snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.TEMPORARY_DQ_OBJECTS TO ROLE PUBLIC;" --connection default
snow sql -q "GRANT USAGE ON STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER TO ROLE PUBLIC;" --connection default

# Step 6: Verify deployment
echo "📋 Step 6: Verifying deployment..."
snow sql -q "SHOW STREAMLITS IN SCHEMA DATA_QUALITY.CONFIG;" --connection default

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🎉 Your Data Quality Manager is now available at:"
echo "   Database: DATA_QUALITY"
echo "   Schema: CONFIG" 
echo "   Streamlit App: DATA_QUALITY_MANAGER"
echo ""
echo "📝 Next steps:"
echo "   1. Open your Snowflake account"
echo "   2. Navigate to Streamlit Apps"
echo "   3. Find and open DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER"
echo "   4. Edit the app to configure your databases in line 21 of streamlit_app.py"
echo ""
echo "🔗 Access your app directly at:"
echo "   https://app.snowflake.com/[your-account]/w/[your-org]/streamlit-apps/DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER"
