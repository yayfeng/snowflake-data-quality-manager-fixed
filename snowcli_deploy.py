#!/usr/bin/env python3
"""
Data Quality Manager SnowCLI Deployment Script
This script automates the deployment of the Data Quality Manager using SnowCLI
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"📋 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if SnowCLI is installed
    try:
        subprocess.run(["snow", "--version"], check=True, capture_output=True)
        print("✅ SnowCLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ SnowCLI is not installed. Please install it first:")
        print("pip install snowflake-cli-labs")
        return False
    
    # Check if required files exist
    required_files = [
        "install.sql",
        "streamlit_app.py", 
        "snowflake_conn.py",
        "utility_functions.py",
        "utility_functions_non_stat.py"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file {file} not found")
            return False
    
    print("✅ All required files found")
    return True

def setup_connection():
    """Setup Snowflake connection"""
    print("\n📋 Setting up Snowflake connection...")
    print("Please configure your connection using one of these methods:")
    print("1. Environment variables:")
    print("   export SNOWFLAKE_ACCOUNT=your_account")
    print("   export SNOWFLAKE_USER=your_username") 
    print("   export SNOWFLAKE_PASSWORD=your_password")
    print("   export SNOWFLAKE_ROLE=your_role")
    print("   export SNOWFLAKE_WAREHOUSE=your_warehouse")
    print("")
    print("2. Or run: snow connection add --connection-name default")
    print("")
    
    response = input("Have you configured your connection? (y/n): ")
    return response.lower() == 'y'

def deploy_database_objects():
    """Deploy database objects using install.sql"""
    print("\n📋 Step 1: Creating database objects...")
    
    # Read and execute install.sql
    if not run_command("snow sql -f install.sql", "Executing install.sql"):
        return False
    
    print("✅ Database objects created successfully")
    return True

def upload_files():
    """Upload files to Snowflake stage"""
    print("\n📋 Step 2: Uploading application files...")
    
    # Create stage if it doesn't exist
    run_command("snow object stage create DATA_QUALITY.CONFIG.CODE --if-not-exists", 
                "Creating stage")
    
    # Upload main files
    files_to_upload = [
        ("streamlit_app.py", "@DATA_QUALITY.CONFIG.CODE"),
        ("snowflake_conn.py", "@DATA_QUALITY.CONFIG.CODE"),
        ("utility_functions.py", "@DATA_QUALITY.CONFIG.CODE"),
        ("utility_functions_non_stat.py", "@DATA_QUALITY.CONFIG.CODE")
    ]
    
    for file, stage in files_to_upload:
        if not run_command(f"snow object stage put {file} {stage} --overwrite", 
                          f"Uploading {file}"):
            return False
    
    # Upload src directory
    src_path = Path("src")
    if src_path.exists():
        for py_file in src_path.glob("*.py"):
            if not run_command(f"snow object stage put {py_file} @DATA_QUALITY.CONFIG.CODE/src/ --overwrite",
                              f"Uploading {py_file}"):
                return False
    
    # Upload stored procedure packages
    sp_dirs = [
        "DATA_QUALITYCONFIGdq_anomaly_detection_sproc_1183842436314279374",
        "DATA_QUALITYCONFIGdq_non_stat_sproc_8775928960113803498"
    ]
    
    for sp_dir in sp_dirs:
        sp_path = Path(sp_dir)
        if sp_path.exists():
            for file in sp_path.iterdir():
                if file.is_file():
                    target_stage = f"@DATA_QUALITY.CONFIG.CODE/{sp_dir}/"
                    run_command(f"snow object stage put {file} {target_stage} --overwrite",
                               f"Uploading {file}")
    
    print("✅ Files uploaded successfully")
    return True

def create_streamlit_app():
    """Create the Streamlit application"""
    print("\n📋 Step 3: Creating Streamlit application...")
    
    # Create Streamlit app using SQL command since SnowCLI streamlit deploy might not work directly
    streamlit_sql = """
    CREATE OR REPLACE STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER
    ROOT_LOCATION = '@DATA_QUALITY.CONFIG.CODE'
    MAIN_FILE = '/streamlit_app.py'
    QUERY_WAREHOUSE = COMPUTE_WH
    COMMENT = '{"origin": "sf_sit","name": "sit_data_quality_framework","version": "{major: 2, minor: 0}"}';
    """
    
    # Write SQL to temp file
    with open("create_streamlit.sql", "w") as f:
        f.write(streamlit_sql)
    
    if not run_command("snow sql -f create_streamlit.sql", "Creating Streamlit app"):
        return False
    
    # Clean up temp file
    os.remove("create_streamlit.sql")
    
    print("✅ Streamlit application created successfully")
    return True

def setup_permissions():
    """Setup permissions for the application"""
    print("\n📋 Step 4: Setting up permissions...")
    
    permissions_sql = """
    GRANT USAGE ON DATABASE DATA_QUALITY TO ROLE PUBLIC;
    GRANT USAGE ON SCHEMA DATA_QUALITY.CONFIG TO ROLE PUBLIC;
    GRANT USAGE ON SCHEMA DATA_QUALITY.RESULTS TO ROLE PUBLIC;
    GRANT USAGE ON SCHEMA DATA_QUALITY.TEMPORARY_DQ_OBJECTS TO ROLE PUBLIC;
    GRANT USAGE ON STREAMLIT DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER TO ROLE PUBLIC;
    """
    
    with open("setup_permissions.sql", "w") as f:
        f.write(permissions_sql)
    
    success = run_command("snow sql -f setup_permissions.sql", "Setting up permissions")
    os.remove("setup_permissions.sql")
    
    if success:
        print("✅ Permissions configured successfully")
    return success

def verify_deployment():
    """Verify the deployment was successful"""
    print("\n📋 Step 5: Verifying deployment...")
    
    if run_command("snow sql -q 'SHOW STREAMLITS IN SCHEMA DATA_QUALITY.CONFIG;'", 
                   "Checking Streamlit apps"):
        print("✅ Deployment verified successfully")
        return True
    return False

def main():
    """Main deployment function"""
    print("🚀 Data Quality Manager SnowCLI Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Setup connection
    if not setup_connection():
        print("❌ Connection setup required. Exiting.")
        sys.exit(1)
    
    # Deploy components
    steps = [
        deploy_database_objects,
        upload_files,
        create_streamlit_app,
        setup_permissions,
        verify_deployment
    ]
    
    for step in steps:
        if not step():
            print(f"❌ Deployment failed at step: {step.__name__}")
            sys.exit(1)
    
    # Success message
    print("\n" + "=" * 50)
    print("✅ Deployment completed successfully!")
    print("")
    print("🎉 Your Data Quality Manager is now available!")
    print("")
    print("📝 Next steps:")
    print("   1. Open your Snowflake account")
    print("   2. Navigate to Streamlit Apps") 
    print("   3. Find and open DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER")
    print("   4. Edit the app to configure your databases in line 21:")
    print("      st.session_state.databases = ['YOUR_DATABASE_1', 'YOUR_DATABASE_2']")
    print("")
    print("🔗 App location: DATA_QUALITY.CONFIG.DATA_QUALITY_MANAGER")

if __name__ == "__main__":
    main()
