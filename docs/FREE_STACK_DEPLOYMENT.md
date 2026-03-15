# AI Trading Platform - Free Cloud Deployment Guide

This guide followed the "Zero-Cost Staging" strategy using Vercel, Koyeb, Render, Supabase, and Upstash.

## Prerequisites
- A GitHub account with the code pushed.
- Signups for: Vercel, Koyeb, Render, Supabase, Upstash.

---

## 1. Supabase (PostgreSQL) — The Database
Supabase provides a hosted PostgreSQL database. We will use it to store your trades, positions, and user data.

### Step-by-Step setup:
1. **Sign Up**: Go to **[supabase.com](https://supabase.com)** and click **"Start your project"**. Sign in using your **GitHub account**.
2. **Create Organization**: If it's your first time, follow the prompts to create a free organization.
3. **New Project**:
   - Click the **"New Project"** button.
   - **Name**: Enter `ai-trading-platform`.
   - **Database Password**: Click **"Generate a password"** and **SAVE IT IMMEDIATELY** in a safe place. You will need this for the connection string.
   - **Region**: Select the region closest to you (e.g., `South Asia (Mumbai)` or `Southeast Asia (Singapore)`).
   - **Pricing Plan**: Ensure **"Free"** is selected.
   - Click **"Create new project"**.
4. **Wait for Provisioning**: It will take about 1-2 minutes for the database to be ready.
5. **Get Connection String**:
   - Once the project is ready, click on the **"Settings"** icon (gear icon at the bottom of the left sidebar).
   - Click on **"Database"** under the "Project Settings" menu.
   - Scroll down to the **"Connection string"** section.
   - Select the **"URI"** tab.
   - You will see a string like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`
   - **Copy this string**. Replace `[YOUR-PASSWORD]` with the password you generated in step 3.
6. **Save**: Keep this full string ready; you will paste it as `DATABASE_URL` when we set up the Koyeb backend.

## 2. Upstash (Redis)
1. Go to **[upstash.io](https://upstash.io)** → "Create Database".
2. Choose a region close to your users (e.g., Mumbai/Singapore).
3. Copy the **REDIS_URL**.
4. Save this for the `REDIS_URL` in Koyeb.

## 3. Render (ML Service)
1. Go to **[render.com](https://render.com)** → "New +" → "Web Service".
2. Connect your GitHub repository.
3. Configure:
   - **Root Directory**: `ml_service`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`
4. Add Environment Variable: `PORT = 8001`.
5. Deploy and copy your URL: `https://your-ml-app.onrender.com`.

## 4. Koyeb (Backend API)
1. Go to **[koyeb.com](https://koyeb.com)** → "Create App".
2. Connect your GitHub repository.
3. Configure:
   - **Root Directory**: `backend`
   - **Builder**: `Dockerfile`
   - **Port**: `8000`
4. Add these Environment Variables:
   - `DATABASE_URL`: (from Supabase)
   - `REDIS_URL`: (from Upstash)
   - `ML_SERVICE_URL`: (from Render)
   - `SECRET_KEY`: (a long random string)
5. Deploy and copy your URL: `https://your-backend.koyeb.app`.

## 5. Vercel (Frontend Dashboard)
1. Go to **[vercel.com](https://vercel.com)** → "Add New Project".
2. Import your repository.
3. Configure:
   - **Root Directory**: `frontend`
4. Add Environment Variables:
   - `REACT_APP_API_URL`: (your Koyeb URL)
   - `REACT_APP_WS_URL`: (your Koyeb URL replaced with `wss://.../ws`)
5. Click **Deploy**.

---

## Post-Deployment Checklist
- [ ] Verify the frontend loads at the Vercel URL.
- [ ] Ensure stock data appears in the watchlist.
- [ ] Verify AI signals load (may take 30s for Render to wake up).
- [ ] Test placing an order to confirm DB connectivity.
