# Deployment Guide

## Frontend Deployment (Netlify)

### Option 1: Deploy via Netlify UI (Recommended)

1. **Sign up/Login to Netlify**
   - Go to https://www.netlify.com/
   - Sign up or login with GitHub

2. **Connect Repository**
   - Click "Add new site" → "Import an existing project"
   - Choose "GitHub" and authorize Netlify
   - Select your repository: `Predict-the-Stock-Market-`

3. **Configure Build Settings**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
   - Click "Deploy site"

4. **Set Environment Variables**
   - Go to Site settings → Environment variables
   - Add: `REACT_APP_API_URL` = `your-backend-url`
   - Click "Save"

5. **Redeploy**
   - Go to Deploys → Trigger deploy → Deploy site

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize Netlify in your project
netlify init

# Deploy
netlify deploy --prod
```

### Frontend URL
After deployment, you'll get a URL like:
```
https://your-site-name.netlify.app
```

---

## Backend Deployment Options

Since Netlify only hosts static sites, you need to deploy the FastAPI backend separately:

### Option 1: Render (Free Tier Available) ⭐ RECOMMENDED

**Steps:**
1. Go to https://render.com/
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - Name: `trading-dashboard-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free
6. Add Environment Variables:
   ```
   DATABASE_URL=your-database-url
   SECRET_KEY=your-secret-key
   REDIS_HOST=your-redis-host (optional)
   ```
7. Click "Create Web Service"

**Free Tier:**
- 750 hours/month
- Automatic HTTPS
- Auto-deploy from GitHub

### Option 2: Railway (Free Tier Available)

**Steps:**
1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add services:
   - Python app (auto-detected)
   - PostgreSQL database
   - Redis (optional)
6. Set environment variables
7. Deploy

**Free Tier:**
- $5 credit/month
- Automatic HTTPS
- Built-in database

### Option 3: Heroku (Paid)

**Steps:**
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

### Option 4: DigitalOcean App Platform

**Steps:**
1. Go to https://www.digitalocean.com/
2. Create new App
3. Connect GitHub repository
4. Configure Python app
5. Add database and Redis
6. Deploy

**Cost:** Starting at $5/month

### Option 5: AWS (EC2 + RDS)

For production-grade deployment with full control.

**Cost:** Variable, starting ~$10-20/month

---

## Complete Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Netlify)              │
│   https://your-app.netlify.app         │
│                                         │
│   - React App                           │
│   - Static Files                        │
│   - CDN Distribution                    │
└─────────────┬───────────────────────────┘
              │
              │ API Calls
              ▼
┌─────────────────────────────────────────┐
│      Backend (Render/Railway)           │
│   https://your-api.onrender.com        │
│                                         │
│   - FastAPI Server                      │
│   - ML Models                           │
│   - Business Logic                      │
└─────────────┬───────────────────────────┘
              │
              ├──────────────┬─────────────┐
              ▼              ▼             ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │PostgreSQL│   │  Redis  │   │ Yahoo   │
         │ Database │   │  Cache  │   │ Finance │
         └─────────┘   └─────────┘   └─────────┘
```

---

## Environment Variables Setup

### Frontend (.env for Netlify)
```env
REACT_APP_API_URL=https://your-api.onrender.com
```

### Backend (.env for Render/Railway)
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_DB=0
```

---

## Post-Deployment Steps

### 1. Update Frontend API URL
After deploying backend, update frontend environment variable:
- Netlify: Site settings → Environment variables
- Set `REACT_APP_API_URL` to your backend URL
- Redeploy frontend

### 2. Configure CORS
Update `main.py` with your Netlify URL:
```python
origins = [
    "https://your-app.netlify.app",
    "http://localhost:3000",  # for local development
]
```

### 3. Run Database Migrations
```bash
# On Render/Railway console
alembic upgrade head
```

### 4. Create Initial User
```bash
# On Render/Railway console
python create_user.py
```

### 5. Test Deployment
- Visit your Netlify URL
- Try logging in
- Check if API calls work
- Test real-time data fetching

---

## Monitoring & Maintenance

### Netlify
- Build logs: Deploys tab
- Analytics: Analytics tab
- Custom domain: Domain settings

### Render/Railway
- Logs: Logs tab
- Metrics: Metrics tab
- Database backups: Database settings

---

## Cost Estimation

### Free Tier Setup:
- **Netlify**: Free (100GB bandwidth/month)
- **Render**: Free (750 hours/month)
- **Total**: $0/month

### Paid Setup (Recommended for Production):
- **Netlify Pro**: $19/month
- **Render Starter**: $7/month
- **PostgreSQL**: $7/month
- **Redis**: $10/month
- **Total**: ~$43/month

---

## Troubleshooting

### Frontend Issues
- **Build fails**: Check Node version (use 18)
- **API calls fail**: Check CORS and API URL
- **404 errors**: Ensure `_redirects` file exists

### Backend Issues
- **Database connection**: Check DATABASE_URL
- **Import errors**: Ensure all dependencies in requirements.txt
- **Port binding**: Use `$PORT` environment variable

---

## Quick Deploy Commands

### Deploy Frontend to Netlify
```bash
cd frontend
npm run build
netlify deploy --prod
```

### Deploy Backend to Render
```bash
# Push to GitHub (auto-deploys)
git add .
git commit -m "Deploy to production"
git push origin main
```

---

## Custom Domain Setup

### Netlify
1. Go to Domain settings
2. Add custom domain
3. Update DNS records
4. Enable HTTPS

### Render
1. Go to Settings → Custom Domains
2. Add your domain
3. Update DNS CNAME record
4. HTTPS auto-enabled

---

## Security Checklist

- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Use environment variables (never commit secrets)
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Regular backups
- [ ] Update dependencies regularly

---

## Support

For deployment issues:
- Netlify: https://docs.netlify.com/
- Render: https://render.com/docs
- Railway: https://docs.railway.app/

---

**Ready to deploy!** 🚀

Choose your backend platform (Render recommended for free tier), then deploy frontend to Netlify.
