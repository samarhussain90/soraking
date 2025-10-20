# Viral Hook Generator

Generate scroll-stopping 12-second viral hooks for any affiliate marketing vertical using Gemini 2.5 and Sora 2 Pro.

## Overview

**Input**: Any product/offer video or URL
**Output**: 4 viral hook variations (12s each) optimized for TikTok, Instagram Reels
**Time**: ~5 minutes fully automated

## Features

- **AI Video Analysis**: Gemini 2.5 extracts complete breakdown (product, benefits, target audience)
- **4 Hook Variations**: Soft, Medium, Aggressive, Ultra intensity levels
- **Extreme Visual Hooks**: NO talking heads - pure visual storytelling for maximum scroll-stopping power
- **Multi-Platform**: 9:16 (TikTok/Reels), 1:1 (Instagram Feed), 16:9 (YouTube)
- **Works For Any Vertical**: Ecommerce, courses, crypto, health, insurance, solar, SaaS
- **Parallel Generation**: All hooks generate simultaneously
- **Pure Sora 2 Pro**: Text overlays, audio, and effects baked directly into prompts

## Installation

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install ffmpeg (for video assembly)
brew install ffmpeg  # macOS
```

### 2. Set API Keys

Already configured in `.env`:
- `OPENAI_API_KEY` - For Sora video generation
- `GEMINI_API_KEY` - For video analysis

## Usage

### Quick Start

```bash
# Clone an ad with all 4 variations
python cli.py path/to/winning_ad.mp4
```

### Advanced Options

```bash
# Generate specific variants only
python cli.py video.mp4 --variants soft aggressive

# Analyze only (no video generation)
python cli.py video.mp4 --analyze-only

# Use Python directly
python ad_cloner.py path/to/video.mp4
```

## Project Structure

```
soraking/
├── config.py                  # Configuration & API keys
├── ad_cloner.py               # Main orchestrator
├── cli.py                     # Command-line interface
├── modules/
│   ├── gemini_analyzer.py     # Gemini 2.5 video analysis
│   ├── aggression_variants.py # Generate 4 aggression levels
│   ├── sora_prompt_builder.py # Advanced prompt engineering
│   ├── sora_client.py         # Parallel Sora API calls
│   └── video_assembler.py     # ffmpeg video stitching
├── templates/
│   └── aggression_presets.json # 4 aggression definitions
└── output/
    ├── analysis/              # Gemini analysis JSON files
    ├── videos/                # Generated videos by variant
    └── logs/                  # Processing logs
```

## Aggression Levels

### 1. Soft (Consultative)
- Calm, educational, warm
- Slower pacing, thoughtful
- Natural lighting, ambient music

### 2. Medium (Professional)
- Confident, direct, balanced
- Moderate pacing, steady
- Clean lighting, professional tone

### 3. Aggressive (Urgent)
- Intense, high-energy, compelling
- Fast cuts, rapid delivery
- High contrast, driving music

### 4. Ultra (Disruptive)
- Confrontational, explosive
- Rapid cuts, relentless pace
- Bold visuals, loud music

## How It Works

### Pipeline

1. **Gemini Analysis** (2-3 min)
   - Uploads video to Gemini 2.5
   - Extracts: spokesperson description, full script, scene breakdown, visual style
   - Saves comprehensive JSON analysis

2. **Variant Generation** (instant)
   - Applies 4 aggression presets to original analysis
   - Same script, different emotional intensity

3. **Prompt Building** (instant)
   - Converts each scene to advanced Sora prompts
   - Uses timestamp segmentation, evolution words, motion verbs
   - Maintains character consistency across scenes

4. **Sora Generation** (15-20 min)
   - Generates 16-20 scenes in parallel (4 variants × 4-5 scenes)
   - Monitors progress for all jobs
   - Downloads completed videos

5. **Assembly** (1-2 min)
   - Stitches scenes into final 48-60s ads
   - One complete ad per aggression level

### Advanced Prompting Techniques

The platform uses 5 advanced Sora techniques:

1. **Timestamp Segmentation**: `[00:00-00:04]` precise scene control
2. **Prompt Chaining**: "gradually evolves into", "morphs into"
3. **Parallel Framing**: Foreground/background depth
4. **Motion Language**: "drifts", "surges", "spirals"
5. **Emotional Continuity**: Smooth emotion transitions

## Cost Estimates

Per full run (4 variants):
- **Gemini 2.5**: ~$0.05 (video analysis)
- **Sora 2 Pro**: ~$5-10 (16-20 clips @ $0.30-0.50 each)
- **Total**: ~$6-11 for 4 testable ads

## Testing Workflow

1. Generate 4 variations
2. Deploy all 4 in ad platform (Meta, TikTok, etc.)
3. A/B test performance
4. Scale the winner

## Examples

```bash
# Analyze a competitor ad
python cli.py competitor_ad.mp4 --analyze-only

# Generate just soft and aggressive
python cli.py winning_ad.mp4 --variants soft aggressive

# Full pipeline with all 4
python cli.py best_performing_ad.mp4
```

## Output

After completion, check `output/` directory:

```
output/
├── analysis/
│   └── analysis_20250112_143022.json
├── videos/
│   ├── soft/
│   │   └── final_soft.mp4
│   ├── medium/
│   │   └── final_medium.mp4
│   ├── aggressive/
│   │   └── final_aggressive.mp4
│   └── ultra/
│       └── final_ultra.mp4
└── results.json
```

## Requirements

- Python 3.9+
- ffmpeg (for video assembly)
- OpenAI API key (Sora access)
- Google Gemini API key

## Troubleshooting

### "ffmpeg not found"
```bash
brew install ffmpeg  # macOS
```

### "API key not found"
Check `.env` file has correct keys

### Video generation fails
- Check Sora API quota/limits
- Verify video resolution support (1792x1024)
- Try shorter duration (reduce to 8s clips)

## Future Enhancements

- [ ] Voice cloning with OpenAI TTS
- [ ] Text overlay system
- [ ] Multi-vertical templates
- [ ] Performance tracking integration
- [ ] Batch processing mode

## License

MIT

## Credits

Built with:
- Google Gemini 2.5 (video analysis)
- OpenAI Sora 2 Pro (video generation)
- ffmpeg (video processing)
