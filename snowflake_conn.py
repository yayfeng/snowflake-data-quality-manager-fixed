import os
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session


def init_snowpark_session(connection_name: str = "snowflake") -> Session:
    """
    Initialize Snowpark session for local development.
    
    Args:
        connection_name: Name of the Snowflake connection in Streamlit secrets
        
    Returns:
        Snowpark Session object
    """
    try:
        # Try to get active session first (for Snowflake-hosted Streamlit)
        session = get_active_session()
        return session
    except:
        # Fall back to connection parameters for local development
        try:
            # Use Streamlit connection
            session = st.connection(connection_name).session()
            return session
        except Exception as e:
            # Last resort - try environment variables or secrets
            connection_parameters = {
                "account": st.secrets.get("account") or os.getenv("SNOWFLAKE_ACCOUNT"),
                "user": st.secrets.get("user") or os.getenv("SNOWFLAKE_USER"),
                "password": st.secrets.get("password") or os.getenv("SNOWFLAKE_PASSWORD"),
                "role": st.secrets.get("role") or os.getenv("SNOWFLAKE_ROLE"),
                "warehouse": st.secrets.get("warehouse") or os.getenv("SNOWFLAKE_WAREHOUSE"),
                "database": st.secrets.get("database") or os.getenv("SNOWFLAKE_DATABASE"),
                "schema": st.secrets.get("schema") or os.getenv("SNOWFLAKE_SCHEMA")
            }
            
            # Remove None values
            connection_parameters = {k: v for k, v in connection_parameters.items() if v is not None}
            
            if not connection_parameters.get("account"):
                raise Exception("No Snowflake connection parameters found. Please configure Streamlit secrets or environment variables.")
            
            session = Session.builder.configs(connection_parameters).create()
            return session
