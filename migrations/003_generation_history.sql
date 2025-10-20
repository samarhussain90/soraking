-- Migration: Generation History System
-- Description: Tables for storing all generations, variants, and videos

-- Generations table - tracks each generation job
CREATE TABLE IF NOT EXISTS generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_video_url TEXT NOT NULL,
    source_video_type VARCHAR(50), -- 'url', 'upload', 'file'
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    total_variants INTEGER NOT NULL,
    variant_types TEXT[] NOT NULL, -- array like ['soft', 'medium', 'aggressive']
    cost_estimate DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Variants table - each variant (soft, medium, aggressive, ultra)
CREATE TABLE IF NOT EXISTS variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
    variant_type VARCHAR(50) NOT NULL, -- soft, medium, aggressive, ultra
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    scenes_completed INTEGER DEFAULT 0,
    total_scenes INTEGER DEFAULT 4,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Scenes table - individual video scenes
CREATE TABLE IF NOT EXISTS scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID NOT NULL REFERENCES variants(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL, -- 1, 2, 3, 4
    sora_prompt TEXT NOT NULL,
    sora_video_id VARCHAR(255), -- Sora API video ID
    sora_status VARCHAR(50), -- queued, processing, completed, failed
    video_url TEXT, -- DigitalOcean Spaces URL
    thumbnail_url TEXT,
    duration INTEGER, -- seconds
    resolution VARCHAR(50), -- e.g., "1920x1080"
    file_size BIGINT, -- bytes
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Metadata table - stores analysis and processing data
CREATE TABLE IF NOT EXISTS generation_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
    original_analysis JSONB, -- Video analysis data
    transformation_data JSONB, -- Ad transformation
    prompts_data JSONB, -- Generated prompts
    evaluation_data JSONB, -- Evaluation results
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_generations_status ON generations(status);
CREATE INDEX IF NOT EXISTS idx_generations_created_at ON generations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_variants_generation_id ON variants(generation_id);
CREATE INDEX IF NOT EXISTS idx_variants_status ON variants(status);
CREATE INDEX IF NOT EXISTS idx_scenes_variant_id ON scenes(variant_id);
CREATE INDEX IF NOT EXISTS idx_scenes_status ON scenes(status);
CREATE INDEX IF NOT EXISTS idx_metadata_generation_id ON generation_metadata(generation_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_generations_updated_at BEFORE UPDATE ON generations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_variants_updated_at BEFORE UPDATE ON variants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_metadata_updated_at BEFORE UPDATE ON generation_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (for future multi-user support)
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_metadata ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for now, can restrict by user later)
CREATE POLICY "Allow all operations on generations" ON generations FOR ALL USING (true);
CREATE POLICY "Allow all operations on variants" ON variants FOR ALL USING (true);
CREATE POLICY "Allow all operations on scenes" ON scenes FOR ALL USING (true);
CREATE POLICY "Allow all operations on metadata" ON generation_metadata FOR ALL USING (true);
