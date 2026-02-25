# Production Deployment Guide

## Frontend Deployment (Vercel/Netlify)

### Build the frontend:
```bash
cd frontend
npm run build
```

### Environment Variables:
- `VITE_API_URL`: Your backend API URL (e.g., https://api.yourapp.com)

### Deploy to Vercel:
```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

## Backend Deployment (AWS/Railway/Render)

### 1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set environment variables:
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend URLs
  Example: `https://yourapp.com,https://www.yourapp.com`

### 3. Run with Gunicorn (production server):
```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Deploy to Railway:
1. Create account at railway.app
2. Connect GitHub repo
3. Set environment variables
4. Deploy automatically

### Deploy to Render:
1. Create account at render.com
2. Create new Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## Docker Deployment (Optional)

### Backend Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
```

## Production Checklist

- [ ] Update CORS origins in backend
- [ ] Set VITE_API_URL in frontend
- [ ] Build frontend with `npm run build`
- [ ] Test production build locally
- [ ] Set up SSL/HTTPS certificates
- [ ] Configure domain names
- [ ] Set up monitoring (optional)
- [ ] Enable error logging
- [ ] Test all API endpoints
- [ ] Verify mobile responsiveness

## Performance Optimization

1. **Frontend**: Already optimized with Vite build
2. **Backend**: Use Gunicorn with multiple workers
3. **Database**: Consider caching frequently accessed data
4. **CDN**: Use CDN for static assets (images)

## Security

- HTTPS only in production
- Restrict CORS to specific domains
- Rate limiting (optional)
- Input validation (already implemented)
