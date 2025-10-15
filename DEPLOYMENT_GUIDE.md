# SoraKing Ad Cloner - Production Deployment Guide

## Overview
This guide will help you deploy the SoraKing Ad Cloner application to production using DigitalOcean App Platform, with Supabase for database and DigitalOcean Spaces for video storage.

## Prerequisites
All cloud services have been configured and tested:
- ✅ Supabase database created and schema deployed
- ✅ DigitalOcean Spaces bucket created
- ✅ All credentials configured
- ✅ Local integration tested successfully

## Quick Deployment Steps

### 1. Push Code to GitHub

```bash
# Create a new repository on GitHub named 'soraking'
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/soraking.git
git branch -M main
git push -u origin main
```

### 2. Deploy to DigitalOcean App Platform

#### Option A: Using the Web Dashboard

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Select "GitHub" as source
4. Choose your `soraking` repository
5. Configure the app:
   - **Name**: soraking-ad-cloner
   - **Region**: NYC3
   - **Branch**: main
   - **Dockerfile Path**: `Dockerfile`

6. Configure Environment Variables (see below)
7. Click "Create Resources"

#### Option B: Using the CLI (doctl)

```bash
# Install doctl if not already installed
brew install doctl

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml
```

### 3. Configure Environment Variables

In the App Platform settings, add these environment variables:

**Required Secrets** (mark as SECRET):
```
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY_HERE
DO_SPACES_ACCESS_KEY=YOUR_DO_SPACES_ACCESS_KEY_HERE
DO_SPACES_SECRET_KEY=YOUR_DO_SPACES_SECRET_KEY_HERE
```

**Public Values**:
```
SUPABASE_URL=https://douctvwttvkfqbvzdwdj.supabase.co
DO_SPACES_BUCKET=soraking-videos
DO_SPACES_REGION=nyc3
PORT=8080
FLASK_ENV=production
```

### 4. Health Check Configuration

The app includes a health check endpoint at `/api/health` that verifies:
- OpenAI API key is configured
- Gemini API key is configured
- Server is responding

Configure in App Platform:
- **Path**: `/api/health`
- **Initial Delay**: 30 seconds
- **Period**: 10 seconds
- **Timeout**: 5 seconds

### 5. Resource Configuration

Recommended settings for production:
- **Instance Size**: Basic XXS (512MB RAM, 1 vCPU)
  - Can upgrade to Basic XS or Small if needed for parallel processing
- **Instance Count**: 1 (can scale to 3+ for high traffic)
- **HTTP Port**: 8080

## Architecture Overview

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  DigitalOcean App   │
│   Platform (Flask)  │
│   - Video upload    │
│   - Pipeline mgmt   │
│   - WebSocket API   │
└──┬─────────┬───────┘
   │         │
   │         ▼
   │  ┌──────────────┐
   │  │  Supabase DB │
   │  │  - Sessions  │
   │  │  - Events    │
   │  │  - Prompts   │
   │  └──────────────┘
   │
   ▼
┌──────────────────┐
│  DO Spaces (S3)  │
│  - Video storage │
│  - Generated ads │
└──────────────────┘
```

## Database Schema

Already deployed to Supabase:
- `sessions` - Pipeline execution tracking
- `videos` - Uploaded video metadata
- `analyses` - Gemini analysis results
- `prompts` - Sora prompts by variant
- `generated_videos` - Sora output tracking
- `events` - Real-time event logging

## Storage Structure

Videos are organized in DigitalOcean Spaces:
```
soraking-videos/
  └── sessions/
      └── {session_id}/
          ├── upload/
          │   └── {timestamp}_{filename}.mp4
          ├── generated/
          │   └── scene_*.mp4
          └── final/
              └── final_{variant}.mp4
```

## API Endpoints

Once deployed, the following endpoints will be available:

### Health & Status
- `GET /api/health` - System health check
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details

### Upload & Processing
- `POST /api/upload` - Upload video to Spaces
- `POST /api/clone` - Start cloning pipeline
- `POST /api/preview` - Preview prompts without generation

### Real-time Updates
- WebSocket connection at `/` for live progress updates

## Testing the Deployment

### 1. Health Check
```bash
curl https://your-app.ondigitalocean.app/api/health
```

Expected response:
```json
{
  "status": "ok",
  "openai_key_configured": true,
  "gemini_key_configured": true
}
```

### 2. Upload Test
```bash
curl -X POST -F "video=@test_video.mp4" \
  https://your-app.ondigitalocean.app/api/upload
```

### 3. Clone Test
```bash
curl -X POST https://your-app.ondigitalocean.app/api/clone \
  -H "Content-Type: application/json" \
  -d '{"video_path": "/path/to/video.mp4", "variants": ["medium"]}'
```

## Monitoring & Logs

### View Logs
```bash
# Using doctl
doctl apps logs {app-id} --follow

# Or via web dashboard
# https://cloud.digitalocean.com/apps/{app-id}/logs
```

### Key Metrics to Monitor
- Request success rate
- Video upload success
- Sora generation completion rate
- Average processing time per variant
- Database connection health
- Spaces upload success

## Troubleshooting

### Common Issues

**1. "Invalid API key" on Supabase**
- Verify `SUPABASE_ANON_KEY` is correct
- Check key hasn't expired
- Ensure URL matches project

**2. Video upload fails**
- Check Spaces credentials
- Verify bucket exists: `soraking-videos`
- Check file size limits (500MB max)

**3. Sora generation slow**
- Normal: 15-20 minutes for full variant
- Each scene takes 3-5 minutes
- Check OpenAI API limits

**4. Health check failing**
- Verify all environment variables set
- Check container logs for startup errors
- Ensure port 8080 is exposed

## Scaling Considerations

### Horizontal Scaling
- Increase instance count for parallel uploads
- Each instance can handle 1 video at a time
- WebSocket connections distribute across instances

### Vertical Scaling
- Upgrade to larger instance for faster video processing
- Recommended: Basic-S (1GB RAM) for heavy workloads

### Cost Optimization
- Use auto-scaling based on traffic
- Scale down to 0 instances during off-hours
- Monitor Spaces bandwidth usage

## Security Notes

### Secrets Management
- All API keys stored as encrypted secrets in App Platform
- Never commit secrets to git (use `.env.example` template)
- Rotate keys periodically

### Network Security
- All traffic over HTTPS (automatic with App Platform)
- CORS configured for frontend access
- Supabase Row Level Security (RLS) enabled

## Backup & Recovery

### Database Backups
- Supabase automatic daily backups
- Point-in-time recovery available
- Export data via Supabase dashboard

### Video Storage Backups
- Spaces versioning can be enabled
- Cross-region replication available
- Consider archival to Glacier for old videos

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create App Platform deployment
3. ✅ Configure environment variables
4. ✅ Test health endpoint
5. ✅ Run end-to-end test with sample video
6. 📊 Set up monitoring alerts
7. 📈 Configure auto-scaling rules
8. 🔒 Enable additional security features

## Support

For issues:
- Check logs in App Platform dashboard
- Review Supabase logs for database issues
- Monitor Spaces access logs
- Check OpenAI API usage dashboard

## Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Supabase Dashboard](https://supabase.com/dashboard/project/douctvwttvkfqbvzdwdj)
- [Spaces Console](https://cloud.digitalocean.com/spaces/soraking-videos)
- [Application Health](https://your-app.ondigitalocean.app/api/health)
