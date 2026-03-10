# Deployment Guide for Secure Streamlit Dashboard

## Quick Deployment Options

### 1. Streamlit Community Cloud (Easiest)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `secure_dashboard.py` as main file
5. Add environment variables in Advanced Settings:
   - `SECRET_KEY`: Generate a random secret key
   - `ADMIN_USERS`: JSON with username/password hashes

### 2. Railway/Render
1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_secure.txt .
RUN pip install -r requirements_secure.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "secure_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Deploy with environment variables

### 3. Self-hosted with Docker
```bash
# Build and run
docker build -t realm-dashboard .
docker run -p 8501:8501 -e SECRET_KEY="your-secret-key" realm-dashboard
```

## Security Features

✅ **JWT Token Authentication** - Secure session management
✅ **Password Hashing** - SHA256 for password storage  
✅ **Session Management** - Automatic logout after 24 hours
✅ **Environment Variables** - No hardcoded secrets
✅ **URL Token Support** - Shareable secure links

## Production Checklist

- [ ] Change default passwords in `auth.py`
- [ ] Set strong `SECRET_KEY` environment variable
- [ ] Use HTTPS (SSL certificates)
- [ ] Set up backup authentication method
- [ ] Monitor access logs
- [ ] Regular security updates

## Environment Variables

```bash
SECRET_KEY=your-super-secret-random-key-here
```

## Usage

1. Install dependencies: `pip install -r requirements_secure.txt`
2. Set environment variable: `export SECRET_KEY="your-secret-key"`
3. Run: `streamlit run secure_dashboard.py`
4. Login with credentials (default: admin/admin123, user/user123)

**Important**: Change the default passwords before deploying!
