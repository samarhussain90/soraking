# Web Interface Guide

## Overview

The Ad Cloner platform includes a modern web interface with real-time progress tracking, detailed logging, and live updates via WebSockets.

## Starting the Web Server

```bash
python server.py
```

The server will start on `http://localhost:3000` (configurable via PORT in `.env`)

## Features

### 1. **Real-Time Progress Tracking**
- Live updates for each pipeline stage
- Visual progress bars
- Stage status indicators (pending, in progress, completed, failed)
- Individual variant tracking

### 2. **Detailed Logging**
- Real-time log streaming
- Color-coded log levels (info, success, error, warning)
- Timestamp for every event
- Structured data display

### 3. **WebSocket Updates**
- Live connection status
- Instant progress notifications
- No page refresh needed
- Automatic reconnection

### 4. **Variant Monitoring**
- Track all 4 variants simultaneously
- Scene-by-scene progress
- Individual variant status
- Completion tracking

### 5. **Session Management**
- View all previous sessions
- Access historical logs
- Review past analyses
- Replay progress

## Using the Web Interface

### Step 1: Open Browser

Navigate to: `http://localhost:3000`

### Step 2: Enter Video Details

1. **Video Path**: Enter full path to video file or YouTube URL
   - Example: `/Users/name/Desktop/winning_ad.mp4`
   - Example: `https://youtube.com/watch?v=abc123`

2. **Select Variants**: Check which aggression levels to generate
   - Soft (calm, consultative)
   - Medium (professional, balanced)
   - Aggressive (urgent, intense)
   - Ultra (confrontational, explosive)

### Step 3: Start Cloning

Click "Start Cloning" button

The interface will:
1. Create a new session
2. Show all 5 pipeline stages
3. Display real-time progress
4. Stream live logs
5. Track variant generation
6. Show final results

### Step 4: Monitor Progress

Watch the pipeline stages:

**Stage 1: Analysis (2-3 min)**
- Gemini analyzing video
- Progress bar shows upload/processing
- Logs show frame extraction

**Stage 2: Variants (instant)**
- Generating 4 aggression variations
- Quick completion

**Stage 3: Prompts (instant)**
- Building Sora prompts
- Scene-by-scene breakdown

**Stage 4: Generation (15-20 min)**
- 4 variant cards appear
- Each shows individual progress
- Scene completion tracking
- Real-time Sora job updates

**Stage 5: Assembly (1-2 min)**
- Stitching scenes
- Creating final videos
- Progress for each variant

### Step 5: View Results

When complete:
- ✅ Status changes to "Complete"
- ⏱️ Total elapsed time shown
- 📹 Video player for each variant
- 📂 File paths displayed
- 🔄 "Clone Another Ad" button

## API Endpoints

The web interface uses these REST API endpoints:

### GET /api/health
Check API status and configuration

```bash
curl http://localhost:3000/api/health
```

Response:
```json
{
  "status": "ok",
  "openai_key_configured": true,
  "gemini_key_configured": true
}
```

### GET /api/sessions
List all sessions

```bash
curl http://localhost:3000/api/sessions
```

Response:
```json
{
  "sessions": [
    {
      "session_id": "session_1234567890",
      "status": "completed",
      "started_at": "2025-01-12T14:30:00",
      "completed_at": "2025-01-12T14:52:00"
    }
  ]
}
```

### GET /api/sessions/{session_id}
Get session details and progress

```bash
curl http://localhost:3000/api/sessions/session_1234567890
```

Response:
```json
{
  "progress": {
    "session_id": "session_1234567890",
    "status": "completed",
    "current_stage": "assembly",
    "stages": { ... },
    "variants": { ... }
  },
  "events": [ ... ]
}
```

### GET /api/sessions/{session_id}/events
Get session events (with optional filtering)

```bash
curl "http://localhost:3000/api/sessions/session_1234567890/events?since=2025-01-12T14:30:00"
```

### POST /api/clone
Start a new cloning job

```bash
curl -X POST http://localhost:3000/api/clone \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/path/to/video.mp4",
    "variants": ["soft", "aggressive"]
  }'
```

Response:
```json
{
  "session_id": "session_1234567890",
  "status": "started",
  "log_dir": "/path/to/logs/session_1234567890"
}
```

## WebSocket Events

The interface connects via Socket.IO for real-time updates:

### Client → Server

**subscribe**: Subscribe to session updates
```javascript
socket.emit('subscribe', { session_id: 'session_1234567890' });
```

### Server → Client

**connected**: Connection established
```javascript
{
  "message": "Connected to Ad Cloner"
}
```

**pipeline_started**: Pipeline has started
```javascript
{
  "session_id": "session_1234567890"
}
```

**progress_update**: Progress changed
```javascript
{
  "session_id": "session_1234567890",
  "progress": { ... }
}
```

**event**: New log event
```javascript
{
  "session_id": "session_1234567890",
  "event": {
    "timestamp": "2025-01-12T14:30:00",
    "level": "INFO",
    "message": "Stage started: analysis",
    "data": { ... }
  }
}
```

**pipeline_completed**: Pipeline finished successfully
```javascript
{
  "session_id": "session_1234567890",
  "results": { ... }
}
```

**pipeline_failed**: Pipeline encountered error
```javascript
{
  "session_id": "session_1234567890",
  "error": "Error message"
}
```

## Log Files

Each session creates detailed logs in `output/logs/{session_id}/`:

- **pipeline.log**: Main log file (text format)
- **progress.json**: Current progress state
- **events.json**: All events with timestamps

### Accessing Logs

Via web interface:
- Real-time display in UI
- Auto-scrolling log viewer
- Color-coded by level

Via filesystem:
```bash
# View main log
tail -f output/logs/session_*/pipeline.log

# View progress
cat output/logs/session_*/progress.json | jq .

# View events
cat output/logs/session_*/events.json | jq .
```

## Troubleshooting

### Port Already in Use

If port 3000 is busy:

1. Change PORT in `.env`:
   ```
   PORT=8080
   ```

2. Restart server:
   ```bash
   python server.py
   ```

### WebSocket Not Connecting

- Check firewall settings
- Verify server is running
- Check browser console for errors
- Try different browser

### API Errors

Check server logs:
```bash
python server.py
```

Look for error messages in terminal

### Cannot Access Logs

Verify log directory exists:
```bash
ls -la output/logs/
```

Check permissions:
```bash
chmod -R 755 output/
```

## Advanced Usage

### Run Multiple Sessions

Each session is isolated:
- Separate log directories
- Independent progress tracking
- No conflicts

### Monitor from Multiple Browsers

Multiple clients can connect:
- All see same progress
- WebSocket broadcasts to all
- Synchronized updates

### Integration with CI/CD

Use API for automation:

```python
import requests

# Start job
response = requests.post('http://localhost:3000/api/clone', json={
    'video_path': '/path/to/video.mp4',
    'variants': ['soft', 'medium']
})

session_id = response.json()['session_id']

# Poll for completion
while True:
    status = requests.get(f'http://localhost:3000/api/sessions/{session_id}').json()
    if status['progress']['status'] in ['completed', 'failed']:
        break
    time.sleep(10)
```

## Production Deployment

For production use:

1. **Use proper WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k eventlet server:app
   ```

2. **Enable HTTPS**:
   - Use reverse proxy (nginx)
   - Configure SSL certificates

3. **Add authentication**:
   - Implement API keys
   - Add user sessions
   - Rate limiting

4. **Scale WebSocket**:
   - Use Redis for pub/sub
   - Enable sticky sessions
   - Load balancing

## Tips

1. **Keep browser tab open** during generation for real-time updates
2. **Check connection status** indicator (bottom right)
3. **Use Chrome DevTools** to debug WebSocket
4. **Review logs** in output/logs/ for detailed debugging
5. **Bookmark session URLs** to return to past jobs

## Next Steps

- Try generating a single variant first
- Monitor the detailed logs
- Review the progress JSON files
- Experiment with different videos
- Test all 4 aggression levels

The web interface provides complete visibility into the entire ad cloning pipeline!
