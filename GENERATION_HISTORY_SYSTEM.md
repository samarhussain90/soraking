# Generation History System - Production Ready

## Overview

Complete system for saving all ad generation history, downloading videos, and providing library/history features.

## System Architecture

### Phase 1: Database (✅ COMPLETED)

**Tables Created:**
- `generations` - Main generation tracking
- `variants` - Each variant (soft, medium, aggressive, ultra)
- `scenes` - Individual video scenes (4 per variant)
- `generation_metadata` - Stores analysis, prompts, evaluation data

**Features:**
- Automatic timestamps and updates
- Cascade delete (deleting generation removes all related data)
- Row Level Security enabled (for future multi-user)
- Indexed for fast queries

**Migration:** `migrations/003_generation_history.sql`

### Phase 2: Backend API (✅ COMPLETED)

**Files Created:**
1. `generation_manager.py` - Database operations manager
2. `video_storage_manager.py` - Video download and storage
3. `pipeline_integrator.py` - Wraps existing pipeline with history tracking
4. `history_api.py` - REST API endpoints

**Core Functions:**

#### GenerationManager
- `create_generation()` - Create new generation record
- `create_variant()` - Create variant record
- `create_scene()` - Create scene record
- `update_scene()` - Update with video URLs and metadata
- `save_metadata()` - Save analysis/prompts/evaluation
- `get_generation()` - Fetch full generation with all data
- `list_generations()` - List with pagination and filtering
- `delete_generation()` - Delete generation and all related data

#### VideoStorageManager
- `download_sora_video()` - Download from Sora API
- `generate_thumbnail()` - Create thumbnail using ffmpeg
- `get_video_metadata()` - Extract duration, resolution, file size
- `upload_video_to_spaces()` - Upload to DigitalOcean Spaces
- `upload_thumbnail_to_spaces()` - Upload thumbnail
- `process_and_store_video()` - Complete workflow (download → process → upload)

#### PipelineIntegrator
- `start_generation()` - Initialize generation tracking
- `save_analysis_metadata()` - Save video analysis
- `save_transformation_metadata()` - Save transformation data
- `save_prompts_metadata()` - Save Sora prompts
- `save_evaluation_metadata()` - Save evaluation results
- `create_scene_records()` - Create all scene records for variant
- `process_sora_video()` - Download and save Sora video
- `mark_generation_failed()` - Handle failures

### Phase 3: API Endpoints (✅ COMPLETED)

**Endpoints:**

```
GET /api/history/generations
  - List all generations
  - Params: limit, offset, status
  - Returns: Array of generations with variants

GET /api/history/generations/<id>
  - Get detailed generation
  - Returns: Full generation with all variants, scenes, metadata

GET /api/history/generations/<id>/variants
  - Get all variants for a generation
  - Returns: Array of variants with scenes

GET /api/history/variants/<id>/scenes
  - Get all scenes for a variant
  - Returns: Array of scenes with video URLs

DELETE /api/history/generations/<id>
  - Delete generation and all data
  - Returns: Success message

GET /api/history/library
  - Get library view (completed generations only)
  - Params: limit, offset
  - Returns: Formatted library items

GET /api/history/stats
  - Get overall statistics
  - Returns: Counts, costs, totals
```

### Phase 4: Integration (⏳ IN PROGRESS)

**Steps:**

1. **Update server.py:**
   ```python
   from history_api import register_history_api

   # Register history API
   register_history_api(app)
   ```

2. **Update ad_cloner.py workflow:**
   ```python
   from pipeline_integrator import PipelineIntegrator

   # Initialize
   integrator = PipelineIntegrator()

   # Start generation
   generation_id = integrator.start_generation(...)

   # Save analysis
   integrator.save_analysis_metadata(generation_id, analysis)

   # Create scene records
   scene_ids = integrator.create_scene_records(generation_id, variant_type, prompts)

   # Process each Sora video
   integrator.process_sora_video(scene_id, sora_video_id, sora_content_url, ...)
   ```

3. **Error handling:**
   ```python
   try:
       # Pipeline code
       ...
   except Exception as e:
       integrator.mark_generation_failed(generation_id, str(e))
       raise
   ```

### Phase 5: Frontend UI (🔄 NEXT)

**Library Page Features:**
- Grid view of all completed generations
- Video thumbnails for each scene
- Filter by date, variant type, status
- Search by source video
- Download individual videos or entire generation
- Delete generations

**UI Components:**
1. Library grid (generations)
2. Generation detail view (all variants and scenes)
3. Video player modal
4. Download buttons
5. Statistics dashboard

### Phase 6: Video Storage Organization (✅ COMPLETED)

**Spaces Structure:**
```
soraking-videos/
└── generations/
    └── {generation_id}/
        ├── soft/
        │   ├── scene_1.mp4
        │   ├── scene_1_thumb.jpg
        │   ├── scene_2.mp4
        │   ├── scene_2_thumb.jpg
        │   ├── scene_3.mp4
        │   ├── scene_3_thumb.jpg
        │   ├── scene_4.mp4
        │   └── scene_4_thumb.jpg
        ├── medium/
        │   └── ... (same structure)
        ├── aggressive/
        │   └── ... (same structure)
        └── ultra/
            └── ... (same structure)
```

## Data Flow

1. **User starts cloning:**
   - Frontend → `/api/clone`
   - Server creates generation record
   - Returns `generation_id`

2. **Pipeline runs:**
   - Video analysis → Save to `generation_metadata.original_analysis`
   - Transformation → Save to `generation_metadata.transformation_data`
   - Prompts generation → Save to `generation_metadata.prompts_data`
   - For each variant:
     - Create variant record (status: pending)
     - For each scene:
       - Create scene record
       - Submit to Sora API
       - When video ready:
         - Download from Sora
         - Generate thumbnail
         - Upload both to Spaces
         - Update scene record with URLs
         - Update variant progress
   - Evaluation → Save to `generation_metadata.evaluation_data`

3. **User views library:**
   - Frontend → `/api/history/library`
   - Returns all completed generations with video URLs
   - Frontend displays grid with thumbnails
   - Click to view/play/download videos

## Database Schema Details

### generations table
```sql
id UUID PRIMARY KEY
source_video_url TEXT
source_video_type VARCHAR(50)  -- 'url', 'upload', 'file'
status VARCHAR(50)  -- 'pending', 'processing', 'completed', 'failed'
total_variants INTEGER
variant_types TEXT[]  -- ['soft', 'medium', 'aggressive']
cost_estimate DECIMAL(10, 2)
actual_cost DECIMAL(10, 2)
error_message TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
completed_at TIMESTAMP
```

### variants table
```sql
id UUID PRIMARY KEY
generation_id UUID (FK → generations.id)
variant_type VARCHAR(50)
status VARCHAR(50)
scenes_completed INTEGER
total_scenes INTEGER
error_message TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
completed_at TIMESTAMP
```

### scenes table
```sql
id UUID PRIMARY KEY
variant_id UUID (FK → variants.id)
scene_number INTEGER  -- 1, 2, 3, 4
sora_prompt TEXT
sora_video_id VARCHAR(255)
sora_status VARCHAR(50)
video_url TEXT  -- DigitalOcean Spaces URL
thumbnail_url TEXT
duration INTEGER (seconds)
resolution VARCHAR(50)
file_size BIGINT (bytes)
status VARCHAR(50)
error_message TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
completed_at TIMESTAMP
```

### generation_metadata table
```sql
id UUID PRIMARY KEY
generation_id UUID (FK → generations.id)
original_analysis JSONB
transformation_data JSONB
prompts_data JSONB
evaluation_data JSONB
created_at TIMESTAMP
updated_at TIMESTAMP
```

## Production Deployment Checklist

- [x] Database migrations applied
- [x] Generation manager implemented
- [x] Video storage manager implemented
- [x] Pipeline integrator created
- [x] History API endpoints created
- [ ] Server.py updated with history API
- [ ] Ad_cloner.py integrated with pipeline integrator
- [ ] Frontend library UI created
- [ ] End-to-end testing
- [ ] Deploy to production

## Usage Examples

### Create Generation
```python
from pipeline_integrator import PipelineIntegrator

integrator = PipelineIntegrator()

generation_id = integrator.start_generation(
    source_video_url='https://youtube.com/watch?v=...',
    source_video_type='url',
    variant_types=['soft', 'medium', 'aggressive'],
    cost_estimate=15.35
)
```

### Process Sora Video
```python
integrator.process_sora_video(
    scene_id='scene-uuid',
    sora_video_id='video_abc123',
    sora_content_url='https://api.openai.com/v1/videos/abc123/content',
    generation_id='gen-uuid',
    variant_type='medium',
    scene_number=1
)
```

### Fetch Library
```python
from generation_manager import GenerationManager

manager = GenerationManager()
generations = manager.list_generations(limit=20, status='completed')
```

### Get Full Generation
```python
generation = manager.get_generation('gen-uuid')
# Returns: { id, source_video_url, status, variants: [...], metadata: {...} }
```

## Benefits

✅ **Complete History** - Every generation is saved permanently
✅ **Video Library** - All videos downloaded and stored in Spaces
✅ **Fast Access** - Indexed database for quick queries
✅ **Thumbnails** - Auto-generated for visual browsing
✅ **Metadata** - All analysis, prompts, evaluation saved
✅ **Search & Filter** - Easy to find past generations
✅ **Download** - Videos can be downloaded anytime
✅ **Cost Tracking** - Track actual costs per generation
✅ **Error Handling** - Failed generations tracked with error messages
✅ **Scalable** - Database and object storage can handle millions of videos

## Next Steps

1. Update server.py to register history API ✓
2. Integrate pipeline_integrator into ad_cloner.py
3. Build frontend library UI
4. Add video player component
5. Test complete workflow
6. Deploy to production
