import streamlit as st
import requests
import pandas as pd
from io import StringIO
import os
from datetime import datetime, timedelta
import jwt
import hashlib
from functools import wraps

# Configuration - Load from Streamlit secrets
try:
    SECRET_KEY = st.secrets["secret_key"]
    ADMIN_USERS = dict(st.secrets["admin_users"])
    
    # Handle nested secrets (github_token and csv_repo_url might be in admin_users)
    all_secrets = dict(st.secrets)
    
    GITHUB_TOKEN = None
    CSV_REPO_URL = None
    
    # Try to get github_token from root level first, then from admin_users
    if "github_token" in all_secrets:
        GITHUB_TOKEN = st.secrets["github_token"]
    elif "github_token" in ADMIN_USERS:
        GITHUB_TOKEN = ADMIN_USERS["github_token"]
    
    # Try to get csv_repo_url from root level first, then from admin_users
    if "csv_repo_url" in all_secrets:
        CSV_REPO_URL = st.secrets["csv_repo_url"]
    elif "csv_repo_url" in ADMIN_USERS:
        CSV_REPO_URL = ADMIN_USERS["csv_repo_url"]
    
except Exception as e:
    st.error(f"❌ Please configure secrets in Streamlit Community Cloud settings!")
    st.stop()

def generate_token(username):
    """Generate JWT token for authenticated user"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except:
        return None

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
    
    token = st.query_params.get('token') or st.session_state.get('token')
    
    if token and not st.session_state.authenticated:
        username = verify_token(token)
        if username:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.token = token
            st.query_params.clear()
            return True
    
    return st.session_state.authenticated

def login_page():
    """Display login page"""
    st.title("🔐 Realm Analytics - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if username in ADMIN_USERS and ADMIN_USERS[username] == hashed_password:
                token = generate_token(username)
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.token = token
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def require_auth(f):
    """Decorator to require authentication for a function"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not check_authentication():
            login_page()
            return None
        return f(*args, **kwargs)
    return wrapper

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.token = None
    st.rerun()

def show_logout_button():
    """Show logout button in sidebar"""
    if st.session_state.get('authenticated'):
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.sidebar.button("Logout"):
            logout()

def load_csv_from_github():
    """Load CSV files from private GitHub repository"""
    if not GITHUB_TOKEN or not CSV_REPO_URL:
        return None
    
    try:
        # Get list of CSV files from repo
        api_url = CSV_REPO_URL.replace("github.com", "api.github.com/repos")
        api_url = api_url.replace("/tree/main", "/contents")
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            files = response.json()
            csv_files = [f for f in files if f['name'].endswith('.csv')]
            
            if not csv_files:
                st.sidebar.warning("⚠️ No CSV files found in remote repository")
                return None
            
            all_data = []
            for file_info in csv_files:
                # Download each CSV file
                download_url = f"https://raw.githubusercontent.com/{CSV_REPO_URL.split('/')[-2]}/{CSV_REPO_URL.split('/')[-1]}/main/{file_info['name']}"
                csv_response = requests.get(download_url)
                
                if csv_response.status_code == 200:
                    csv_data = csv_response.text
                    df = pd.read_csv(StringIO(csv_data))
                    if not df.empty:
                        # Add filename info
                        df['source_file'] = file_info['name']
                        all_data.append(df)
                        st.sidebar.success(f"✅ Loaded {file_info['name']}")
                else:
                    st.sidebar.error(f"❌ Failed to load {file_info['name']}")
            
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            else:
                return None
        else:
            st.sidebar.error(f"❌ Failed to access repository: {response.status_code}")
            return None
            
    except Exception as e:
        st.sidebar.error(f"❌ Error loading remote CSV files: {e}")
        return None

def load_csv_files():
    """Smart loading: Try local first, fallback to remote if empty"""
    
    # Try local files first
    import glob
    csv_files = glob.glob("Daily Reports/*.csv")
    
    if csv_files:
        st.sidebar.success("💾 Using local CSV files")
        # Let the original dashboard handle local loading
        return None
    
    # Fallback to remote if local is empty
    if GITHUB_TOKEN and CSV_REPO_URL:
        st.sidebar.info("📡 Local files empty, loading from remote repository...")
        remote_df = load_csv_from_github()
        
        if remote_df is not None and not remote_df.empty:
            st.sidebar.success("✅ Using remote CSV files")
            # Save remote data to a temporary location for the original dashboard to read
            os.makedirs("Daily Reports", exist_ok=True)
            remote_df.to_csv("Daily Reports/remote_data.csv", index=False)
            return remote_df
        else:
            st.sidebar.error("❌ Remote files also empty")
    
    # No data available
    st.sidebar.error("❌ No CSV files available locally or remotely")
    return None

@require_auth
def main():
    # Handle authentication and data loading
    show_logout_button()
    
    # Load data with smart fallback
    load_csv_files()
    
    # Import and run the original dashboard
    try:
        # Get the current directory and dashboard path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_path = os.path.join(current_dir, 'dashboard.py')
        
        # Read and execute the dashboard code
        with open(dashboard_path, 'r') as f:
            dashboard_code = f.read()
        
        # Execute the dashboard code in the current namespace
        exec(dashboard_code, globals())
        
    except FileNotFoundError:
        st.error(f"❌ Dashboard file not found at: {dashboard_path}")
        st.info("Please ensure dashboard.py is in the DailyReportTools directory")
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {e}")
        st.info("Please check the dashboard.py file for any syntax errors")

if __name__ == "__main__":
    main()
