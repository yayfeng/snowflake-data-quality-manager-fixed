# Data Quality Manager - SnowCLI Deployment Guide

This guide walks you through deploying the Data Quality Manager to your Snowflake account using SnowCLI.

## Prerequisites

1. **Install SnowCLI**:
   ```bash
   pip install snowflake-cli-labs
   ```

2. **Verify installation**:
   ```bash
   snow --version
   ```

## Deployment Options

### Option 1: Automated Python Script (Recommended)

1. **Run the automated deployment script**:
   ```bash
   python snowcli_deploy.py
   ```

2. **Follow the prompts** to configure your Snowflake connection

### Option 2: Manual SnowCLI Commands

1. **Configure your Snowflake connection**:
   ```bash
   snow connection add --connection-name default
   ```
   Or set environment variables:
   ```bash
   export SNOWFLAKE_ACCOUNT=your_account
   export SNOWFLAKE_USER=your_username
   export SNOWFLAKE_PASSWORD=your_password
   export SNOWFLAKE_ROLE=your_role
   export SNOWFLAKE_WAREHOUSE=your_warehouse
   ```

2. **Deploy database objects**:
   ```bash
   snow sql -f install.sql
   ```

3. **Upload application files**:
   ```bash
   # Create stage
   snow object stage create DATA_QUALITY.CONFIG.CODE --if-not-exists
   
   # Upload main files
   snow object stage put streamlit_app.py @DATA_QUALITY.CONFIG.CODE --overwrite
   snow object stage put snowflake_conn.py @DATA_QUALITY.CONFIG.CODE --overwrite
   snow object stage put utility_functions.py @DATA_QUALITY.CONFIG.CODE --overwrite
   snow object stage put utility_functions_non_stat.py @DATA_QUALITY.CONFIG.CODE --overwrite
   
   # Upload src directory
   snow object stage put src/* @DATA_QUALITY.CONFIG.CODE/src/ --overwrite
   ```

4. **Create Streamlit application**:
   ```bash
   snow sql -q "
   CREATE OR REPLACE STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER
   ROOT_LOCATION = '@DATA_QUALITY.CONFIG.CODE'
   MAIN_FILE = '/streamlit_app.py'
   QUERY_WAREHOUSE = COMPUTE_WH
   COMMENT = '{\"origin\": \"sf_sit\",\"name\": \"sit_data_quality_framework\",\"version\": \"{major: 2, minor: 0}\"}';
   "
   ```

5. **Setup permissions**:
   ```bash
   snow sql -q "GRANT USAGE ON DATABASE DATA_QUALITY TO ROLE PUBLIC;"
   snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.CONFIG TO ROLE PUBLIC;"
   snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.RESULTS TO ROLE PUBLIC;"
   snow sql -q "GRANT USAGE ON SCHEMA DATA_QUALITY.TEMPORARY_DQ_OBJECTS TO ROLE PUBLIC;"
   snow sql -q "GRANT USAGE ON STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER TO ROLE PUBLIC;"
   ```

6. **Verify deployment**:
   ```bash
   snow sql -q "SHOW STREAMLITS IN SCHEMA DATA_QUALITY.CONFIG;"
   ```

### Option 3: Bash Script

1. **Run the bash deployment script**:
   ```bash
   ./deploy_snowcli.sh
   ```

## Post-Deployment Configuration

1. **Access your Streamlit app**:
   - Open your Snowflake account
   - Navigate to "Streamlit Apps"
   - Find and open `DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER`

2. **Configure databases**:
   - Edit the Streamlit app
   - Update line 21 in `streamlit_app.py`:
     ```python
     st.session_state.databases = ["YOUR_DATABASE_1", "YOUR_DATABASE_2"]
     ```
   - Replace with the actual databases you want to monitor

3. **Update warehouse** (if needed):
   - If you're not using `COMPUTE_WH`, update the warehouse name in the Streamlit app creation command

## Troubleshooting

### Common Issues

1. **Connection errors**:
   - Verify your Snowflake credentials
   - Check network connectivity
   - Ensure your role has necessary privileges

2. **Permission errors**:
   - Make sure you have ACCOUNTADMIN or equivalent privileges
   - Check that your role can create databases and schemas

3. **File upload errors**:
   - Ensure all required files are present in the directory
   - Check file permissions

4. **Warehouse not found**:
   - Update `COMPUTE_WH` to your actual warehouse name in:
     - `install.sql` (line 274)
     - Streamlit creation command

### Verification Commands

```bash
# Check if database exists
snow sql -q "SHOW DATABASES LIKE 'DATA_QUALITY';"

# Check if Streamlit app exists
snow sql -q "SHOW STREAMLITS IN SCHEMA DATA_QUALITY.CONFIG;"

# Check stage contents
snow sql -q "LIST @DATA_QUALITY.CONFIG.CODE;"
```

## Support

If you encounter issues:
1. Check the [GitHub repository](https://github.com/Snowflake-Labs/emerging-solutions-toolbox/tree/main/sfguide-getting-started-with-data-quality-manager) for updates
2. Review the error messages carefully
3. Ensure all prerequisites are met
4. Try the manual deployment steps if the automated script fails

## What's Deployed

After successful deployment, you'll have:

- ✅ **DATA_QUALITY database** with all required schemas and tables
- ✅ **Stored procedures** for anomaly detection and non-statistical checks
- ✅ **Streamlit application** for the user interface
- ✅ **Proper permissions** for application access
- ✅ **All Python dependencies** uploaded to Snowflake stages

Your Data Quality Manager is now ready to use!
