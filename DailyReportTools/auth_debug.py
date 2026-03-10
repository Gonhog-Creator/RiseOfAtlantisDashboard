import streamlit as st
import hashlib
import os
import json
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Debug function to check secrets
def debug_secrets():
    """Debug function to check how secrets are loaded"""
    st.write("🔍 Debug Information:")
    
    try:
        # Try to access secrets
        all_secrets = dict(st.secrets)
        st.write("All secrets found:", all_secrets.keys())
        
        if "secret_key" in st.secrets:
            st.write("✅ secret_key found")
        else:
            st.write("❌ secret_key NOT found")
            
        if "admin_users" in st.secrets:
            st.write("✅ admin_users found:", st.secrets["admin_users"])
        else:
            st.write("❌ admin_users NOT found")
            
    except Exception as e:
        st.write(f"❌ Error accessing secrets: {e}")

# Configuration - Load from Streamlit secrets
try:
    # For Streamlit Community Cloud
    SECRET_KEY = st.secrets["secret_key"]
    ADMIN_USERS = dict(st.secrets["admin_users"])
    
    # Debug info
    st.write("🔧 Configuration loaded from Streamlit secrets")
    st.write(f"SECRET_KEY: {SECRET_KEY[:10]}...")
    st.write(f"ADMIN_USERS: {ADMIN_USERS}")
    
except Exception as e:
    st.error(f"Error loading secrets: {e}")
    debug_secrets()
    
    # Fallback for local development
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    # Load users from environment variable or use defaults
    def load_users():
        """Load user credentials from environment variable"""
        users_env = os.getenv("ADMIN_USERS")
        if users_env:
            try:
                return json.loads(users_env)
            except json.JSONDecodeError:
                st.error("Invalid ADMIN_USERS format. Using default users.")
        
        # Default users (for local development)
        return {
            "admin": hashlib.sha256("admin123".encode()).hexdigest(),
            "user": hashlib.sha256("user123".encode()).hexdigest()
        }
    
    ADMIN_USERS = load_users()
    st.write("🔧 Using fallback configuration")

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
    
    # Check for token in URL or session
    token = st.query_params.get('token') or st.session_state.get('token')
    
    if token and not st.session_state.authenticated:
        username = verify_token(token)
        if username:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.token = token
            # Clear token from URL
            st.query_params.clear()
            return True
    
    return st.session_state.authenticated

def login_page():
    """Display login page with debug info"""
    st.title("🔐 Realm Analytics - Login")
    
    # Show debug info
    with st.expander("🔍 Debug Information"):
        debug_secrets()
        st.write(f"Available users: {list(ADMIN_USERS.keys())}")
        
        # Test password hashing
        test_password = "admin123"
        test_hash = hashlib.sha256(test_password.encode()).hexdigest()
        st.write(f"Test hash for '{test_password}': {test_hash}")
        st.write(f"Expected hash for admin: {ADMIN_USERS.get('admin', 'NOT FOUND')}")
        st.write(f"Hashes match: {test_hash == ADMIN_USERS.get('admin')}")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            st.write(f"Attempting login with username: {username}")
            
            # Hash the entered password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            st.write(f"Password hash: {hashed_password}")
            
            # Check if user exists and password matches
            if username in ADMIN_USERS:
                expected_hash = ADMIN_USERS[username]
                st.write(f"Expected hash: {expected_hash}")
                st.write(f"Hashes match: {hashed_password == expected_hash}")
                
                if hashed_password == expected_hash:
                    # Generate and store token
                    token = generate_token(username)
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.token = token
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Password does not match!")
            else:
                st.error(f"User '{username}' not found!")

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
