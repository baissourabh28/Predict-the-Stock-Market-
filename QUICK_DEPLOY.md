# Quick Deployment Guide - Netlify + Render

## 🚀 Deploy in 10 Minutes!

### Step 1: Deploy Backend to Render (5 minutes)

1. **Go to Render**: https://render.com/
2. **Sign up** with your GitHub account
3. Click **"New +"** → **"Web Service"**
4. **Connect** your repository: `Predict-the-Stock-Market-`
5. **Configure**:
   ```
   Name: trading-dashboard-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```
6. **Add Environment Variables**:
   ```
   SECRET_KEY=your-random-secret-key-here
   DATABASE_URL=sqlite:///./trading_dashboard.db
   ```
7. Click **"Create Web Service"**
8. **Wait 3-5 minutes** for deployment
9. **Copy your backend URL**: `https://your-app.onrender.com`

### Step 2: Deploy Frontend to Netlify (5 minutes)

1. **Go to Netlify**: https://www.netlify.com/
2. **Sign up** with your GitHub account
3. Click **"Add new site"** → **"Import an existing project"**
4. Choose **"GitHub"** and authorize Netlify
5. Select repository: **`Predict-the-Stock-Market-`**
6. **Configure**:
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/build
   ```
7. **Add Environment Variable**:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-app.onrender.com` (from Step 1)
8. Click **"Deploy site"**
9. **Wait 2-3 minutes** for deployment
10. **Your app is live!** 🎉

### Step 3: Update CORS (1 minute)

1. Open `main.py` in your repository
2. Update the `origins` list:
   ```python
   origins = [
       "https://your-netlify-url.netlify.app",  # Add your Netlify URL
       "http://localhost:3000",
   ]
   ```
3. Commit and push:
   ```bash
   git add main.py
   git commit -m "Update CORS for production"
   git push origin main
   ```
4. Render will auto-redeploy (wait 2 minutes)

### Step 4: Test Your Deployment

1. Visit your Netlify URL: `https://your-app.netlify.app`
2. Register a new user
3. Login
4. Test the dashboard features
5. Check if stock data loads

---

## 🎯 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://your-app.netlify.app`
- **Backend API**: `https://your-app.onrender.com`
- **API Docs**: `https://your-app.onrender.com/docs`

---

## 💡 Tips

### Free Tier Limitations
- **Render Free**: Spins down after 15 min of inactivity (first request takes ~30s)
- **Netlify Free**: 100GB bandwidth/month, 300 build minutes/month

### Upgrade Options
- **Render Starter**: $7/month (no spin down)
- **Netlify Pro**: $19/month (more bandwidth)

### Custom Domain
Both Netlify and Render support custom domains for free!

---

## 🐛 Troubleshooting

### Backend Issues
- **"Application failed to respond"**: Wait 30s for cold start
- **Database errors**: Check DATABASE_URL in environment variables
- **Import errors**: Ensure requirements.txt is complete

### Frontend Issues
- **API calls fail**: Check REACT_APP_API_URL is correct
- **CORS errors**: Update origins in main.py
- **Build fails**: Check Node version (should be 18)

### Quick Fixes
```bash
# Redeploy backend
git commit --allow-empty -m "Redeploy"
git push origin main

# Redeploy frontend
# Go to Netlify → Deploys → Trigger deploy
```

---

## 📊 Monitoring

### Render Dashboard
- View logs: Logs tab
- Check metrics: Metrics tab
- Restart service: Manual Deploy → Deploy latest commit

### Netlify Dashboard
- View builds: Deploys tab
- Check analytics: Analytics tab
- View logs: Deploy log

---

## 🔒 Security Checklist

- [ ] Set strong SECRET_KEY (use: `openssl rand -hex 32`)
- [ ] Update CORS origins with your Netlify URL
- [ ] Never commit .env files
- [ ] Use HTTPS (automatic on both platforms)
- [ ] Enable Netlify's security headers

---

## 🎉 You're Done!

Your AI-powered trading dashboard is now live and accessible worldwide!

**Share your app**: `https://your-app.netlify.app`

---

## 📞 Need Help?

- Full guide: See `DEPLOYMENT.md`
- Render docs: https://render.com/docs
- Netlify docs: https://docs.netlify.com/
