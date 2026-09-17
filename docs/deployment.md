# Nifty 100 Financial Intelligence Platform — Production Deployment Guide

## 1. Environment & Architecture Overview

- **GitHub Repository**: [https://github.com/SATAPASTI-HARIpRASAD-07/Bluestock_MF_Capstone](https://github.com/SATAPASTI-HARIpRASAD-07/Bluestock_MF_Capstone)
- **Streamlit Dashboard Entry Point**: `dashboard/app.py`
- **FastAPI REST API Entry Point**: `api/main.py` (Vercel Serverless: `api/index.py`)
- **Database Artifact**: `db/nifty100.db` (Auto-generated on cloud container startup via `db/loader.py`)

---

## 2. Deploying Streamlit Dashboard on Streamlit Community Cloud

1. Log in to **[share.streamlit.io](https://share.streamlit.io)** using your GitHub account.
2. Click **New app**.
3. Fill in the deployment form:
   - **Repository**: `SATAPASTI-HARIpRASAD-07/Bluestock_MF_Capstone`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
4. Click **Deploy!**

Streamlit Cloud will read `requirements.txt`, install dependencies, run `dashboard/app.py`, auto-initialize `db/nifty100.db`, and generate your public HTTPS URL (e.g. `https://bluestock-nifty100.streamlit.app`).

---

## 3. Deploying FastAPI REST API on Vercel

1. Log in to **[vercel.com](https://vercel.com)** using your GitHub account.
2. Click **Add New** ➔ **Project**.
3. Import repository: `SATAPASTI-HARIpRASAD-07/Bluestock_MF_Capstone`.
4. Click **Deploy**. Vercel will detect `vercel.json` and route API requests to `/api/index.py`.
5. Public API URL: `https://bluestock-nifty100-api.vercel.app` (Docs at `/docs`).

---

## 4. Local Run Instructions

- **Run Full Build & Test Suite**:
  ```bash
  python scripts/build_all.py
  ```

- **Run Dashboard Locally**:
  ```bash
  streamlit run dashboard/app.py
  ```

- **Run API Locally**:
  ```bash
  uvicorn api.main:app --port 8000
  ```
