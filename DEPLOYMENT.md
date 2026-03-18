# Deployment Guide (Vercel + Render)

## 1) Backend on Render

- Create a new Render Web Service from this repository.
- Render will detect `render.yaml` automatically.
- Set secret env var:
  - `GEMINI_API_KEY` (optional but recommended)
- Deploy and copy backend URL, e.g. `https://your-backend-name.onrender.com`

## 2) Frontend on Vercel

- Import the same repository in Vercel.
- Set project Root Directory to `Frontend`.
- Set environment variable:
  - `NEXT_PUBLIC_API_URL=https://your-backend-name.onrender.com`
- Deploy.

## 3) Verify End-to-End

- Open frontend URL from Vercel.
- Run these demo queries:
  - `show me average price by model`
  - `show me yearly average mileage trend`
  - `now only show automatic transmission top 5`

## 4) CORS

- Backend allows `https://*.vercel.app` by default through `CORS_ORIGIN_REGEX`.
- If you use a custom domain, set `CORS_ORIGINS` accordingly.
