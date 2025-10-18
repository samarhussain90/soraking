# SORAKING REPOSITORY COMPREHENSIVE ANALYSIS

## EXECUTIVE SUMMARY

**Repository**: AD Cloner - AI-powered video ad generator using Gemini 2.5, OpenAI, and Sora
**Architecture**: Pipeline-based orchestrator with 16 specialized modules
**Technology Stack**: Flask/Python backend, vanilla JS frontend, Supabase DB, DigitalOcean Spaces

**Key Issue**: High degree of **CONFIGURATION REDUNDANCY** and **CODE DUPLICATION** across modules, with scattered responsibility patterns and inconsistent data flow handling.

---

## 1. OVERALL ARCHITECTURE

### Core Pipeline Stages
```
Video Upload
    ↓
[1] ANALYSIS (Gemini 2.5)
    ↓
[1.5] TRANSFORMATION (Sora Structure Detection)
    ↓
[2] VARIANT GENERATION (4 Aggression Levels)
    ↓
[3] PROMPT COMPOSITION (SoraPromptBuilder)
    ↓
[4] SORA GENERATION (Parallel Video Creation)
    ↓
[5] ASSEMBLY (Video Stitching)
    ↓
[6] EVALUATION (Gemini Quality Check)
```

### Component Interaction Model

```
        ┌─────────────────────────────────────┐
        │      Flask Web Server               │
        │  (server.py)                        │
        └─────────────────────────────────────┘
                    ↓
        ┌─────────────────────────────────────┐
        │      AdCloner Orchestrator          │
        │  (ad_cloner.py - Main Pipeline)     │
        └─────────────────────────────────────┘
             ↓    ↓    ↓    ↓    ↓    ↓
    ┌──────────────────────────────────────────────────────┐
    │              16 Specialized Modules                  │
    │                                                      │
    │  Analysis Layer:                                     │
    │  - GeminiVideoAnalyzer (gemini_analyzer.py)         │
    │  - SettingsManager (settings_manager.py)            │
    │                                                      │
    │  Transformation Layer:                              │
    │  - SoraAdTransformer (sora_transformer.py)          │
    │  - AggressionVariantGenerator (aggression_variants) │
    │                                                      │
    │  Prompt Generation Layer:                            │
    │  - SoraPromptBuilder (sora_prompt_builder.py)       │
    │  - SoraPromptComposer (sora_prompt_composer.py)     │
    │  - AdDirector (ad_director.py)                      │
    │  - MarketingValidator (marketing_validator.py)      │
    │  - PromptValidator (prompt_validator.py)            │
    │                                                      │
    │  Generation Layer:                                   │
    │  - SoraClient (sora_client.py)                      │
    │  - VideoAssembler (video_assembler.py)              │
    │  - AdEvaluator (ad_evaluator.py)                    │
    │                                                      │
    │  Infrastructure:                                     │
    │  - PipelineLogger (logger.py)                       │
    │  - SupabaseClient (supabase_client.py)              │
    │  - SpacesClient (spaces_client.py)                  │
    │  - ConversionOptimizer (conversion_optimizer.py)    │
    └──────────────────────────────────────────────────────┘
```

---

## 2. MODULE ORGANIZATION & RESPONSIBILITIES

### A. Analysis & Detection Modules

| Module | Responsibility | Dependencies | Lines |
|--------|----------------|--------------|-------|
| `gemini_analyzer.py` | Video analysis using Gemini 2.5 API | genai, requests, config, settings_manager | 300+ |
| `sora_transformer.py` | Vertical detection + scene structure transformation | config | 500+ |
| `settings_manager.py` | Settings CRUD with caching from Supabase | supabase_client | 360 |

### B. Prompt Generation Modules (HEAVILY OVERLAPPING)

| Module | Responsibility | Dependencies | Status |
|--------|----------------|--------------|--------|
| `sora_prompt_builder.py` | Direct prompt building from transformer scenes | config | ACTIVE |
| `sora_prompt_composer.py` | Prompt conversion from AI Director output | NONE | REDUNDANT |
| `ad_director.py` | AI-driven scene generation via OpenAI | openai, config | ACTIVE |
| `marketing_validator.py` | Scene validation + conversion optimization | openai, config | ACTIVE |
| `prompt_validator.py` | Technical validation (length, structure) | NONE | UTILITY |

**ISSUE**: Multiple pathways exist for prompt generation (see Section 4.1)

### C. Generation & Assembly Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `sora_client.py` | Sora API calls + job polling + downloads | openai, requests, config |
| `video_assembler.py` | FFmpeg video stitching | subprocess, pathlib |
| `ad_evaluator.py` | Generated ad quality evaluation | gemini_analyzer, genai |

### D. Variant & Aggression Modules

| Module | Responsibility | Lines |
|--------|----------------|-------|
| `aggression_variants.py` | 4-level variant generation | 300+ |
| `conversion_optimizer.py` | Conversion-focused optimization | ~200 |

### E. Infrastructure & Logging

| Module | Responsibility |
|--------|----------------|
| `logger.py` | Comprehensive pipeline logging + progress tracking |
| `supabase_client.py` | Database operations (sessions, videos, prompts, events) |
| `spaces_client.py` | DigitalOcean S3-compatible storage |
| `settings_manager.py` | Database-backed configuration |

---

## 3. DATA FLOW & PIPELINE ORCHESTRATION

### Complete Flow Diagram

```python
# ad_cloner.py clone_ad() method flow:

1. ANALYSIS
   ├─ analyzer.analyze_and_save(video_path)
   │  └─ Returns: analysis (dict), analysis_path (str)
   ├─ _normalize_spokesperson(analysis) ← DUPLICATION #1
   └─ LOG: scene count, spokesperson details

2. TRANSFORMATION
   ├─ transformer.detect_vertical(analysis)
   ├─ transformer.transform_to_sora_structure(analysis, vertical)
   └─ analysis['scene_breakdown'] = transformed_scenes

3. VARIANT GENERATION
   ├─ variant_generator.generate_variants(analysis)
   │  └─ Calls: _create_variant() for each of 4 levels
   └─ Returns: [soft, medium, aggressive, ultra] variants

4. PROMPT COMPOSITION
   ├─ FROM: SoraPromptBuilder.build_all_scene_prompts()
   │  └─ Direct method: transformer → prompts (NEW)
   ├─ OR: AdDirector.generate_scene_structure() (ALTERNATIVE)
   │  └─ OpenAI method: analysis → scenes → prompts
   ├─ OR: SoraPromptComposer.compose_from_director_scenes() (ALTERNATIVE)
   │  └─ Converts AI Director output
   └─ PromptValidator.validate_all_prompts()

5. SORA GENERATION (PARALLEL)
   ├─ For each variant:
   │  ├─ sora_client.generate_variant_parallel(prompts, variant_level)
   │  │  └─ Creates async jobs for each scene
   │  └─ Polls for completion + downloads videos

6. ASSEMBLY
   ├─ assembler.assemble_variant(variant_result)
   │  └─ Stitches scenes with FFmpeg

7. EVALUATION
   └─ evaluator.evaluate_generated_ad(video_path, analysis, prompts)
```

**CRITICAL ISSUE**: Steps 4 has 3 ALTERNATIVE PATHWAYS that aren't reconciled in current flow.

---

## 4. IDENTIFIED REDUNDANCIES

### 4.1 PROMPT COMPOSITION - Multiple Redundant Pathways

**PROBLEM**: Three competing modules generate prompts from the same data:

```python
# PATHWAY 1: Direct (Current - ad_cloner.py:245-311)
prompt_builder = SoraPromptBuilder()
composed_prompts = prompt_builder.build_all_scene_prompts(
    variant,
    spokesperson_desc,
    full_script
)

# PATHWAY 2: AI Director (Unused in current flow)
ad_director = AdDirector()
scenes = ad_director.generate_scene_structure(
    gemini_analysis,
    variant_data,
    aggression_level
)

# PATHWAY 3: Composer (Unused)
prompt_composer = SoraPromptComposer()
sora_prompts = prompt_composer.compose_from_director_scenes(director_scenes)
```

**Impact**: 
- Unused modules consume maintenance effort
- Inconsistent prompt output formats
- Unclear which method produces better results
- Three different validation approaches

**Modules Involved**: 
- `sora_prompt_builder.py` (ACTIVE)
- `ad_director.py` (INACTIVE)
- `sora_prompt_composer.py` (INACTIVE)
- `marketing_validator.py` (PARTIAL USE)

---

### 4.2 SPOKESPERSON NORMALIZATION - Code Duplication

**PROBLEM**: `_normalize_spokesperson()` exists in TWO places:

```python
# LOCATION 1: ad_cloner.py (lines 52-72)
def _normalize_spokesperson(self, analysis: Dict) -> Dict:
    """Normalize spokesperson data..."""
    spokesperson = analysis.get('spokesperson', {})
    if isinstance(spokesperson, list):
        if len(spokesperson) > 0:
            return spokesperson[0]
        else:
            return {}
    elif isinstance(spokesperson, dict):
        return spokesperson
    else:
        return {}

# LOCATION 2: sora_transformer.py (similar implementation)
def _normalize_spokesperson(self, analysis: Dict) -> Dict:
    """Normalize spokesperson data..."""
    # IDENTICAL LOGIC
```

**Called from**:
- `ad_cloner.py`: lines 109, 261 (2 calls)
- `sora_transformer.py`: line with `original_spokesperson = self._normalize_spokesperson(analysis)`

**Impact**: Maintenance burden, inconsistent updates

**Solution**: Move to utility module

---

### 4.3 CONFIGURATION SCATTERED ACROSS FILES

**PROBLEM**: Configuration values exist in FOUR places:

```python
# CONFIG 1: config.py (centralized)
SORA_MODEL = 'sora-2-pro'
SORA_RESOLUTION = '1792x1024'
SORA_DURATION = '12'

# CONFIG 2: settings_manager.py (database)
def get_sora_config(self) -> Dict:
    setting = self.get_setting('sora_config', 'technical_specs')
    return {
        'resolution': '4K',
        'aspect_ratio': '1792x1024',
        'default_style': 'engaging',
        'default_color_grade': 'cinematic',
        'audio_mix': 'cinematic'
    }

# CONFIG 3: aggression_variants.py (hardcoded defaults)
self.presets = self._get_default_presets()

# CONFIG 4: sora_transformer.py (HOOK_SCENARIOS hardcoded)
HOOK_SCENARIOS = {
    'auto_insurance': [...],
    'health_insurance': [...]
}
```

**Redundant Values**:
- `SORA_RESOLUTION` defined in 3+ places
- `AUDIO_MIX` in config.py AND settings_manager.py
- Default presets in settings AND aggression_variants

**Files Affected**: `config.py`, `settings_manager.py`, `aggression_variants.py`, `sora_transformer.py`

---

### 4.4 CLIENT INITIALIZATION - Repeated Pattern

**PROBLEM**: Three client initialization patterns:

```python
# PATTERN 1: Singleton with global instance (logger.py, settings_manager.py)
_current_logger: Optional[PipelineLogger] = None
def get_logger(session_id: Optional[str] = None) -> PipelineLogger:
    global _current_logger
    if _current_logger is None or session_id:
        _current_logger = PipelineLogger(session_id)
    return _current_logger

# PATTERN 2: Direct instantiation (server.py, ad_cloner.py)
supabase_client = SupabaseClient()
spaces_client = SpacesClient()
sora_client = SoraClient(spaces_client=spaces_client, session_id=session_id)

# PATTERN 3: Try/except with fallback (server.py:26-35)
try:
    supabase_client = SupabaseClient()
    spaces_client = SpacesClient()
    print("✓ Cloud clients initialized")
except Exception as e:
    print(f"⚠ Warning: Cloud clients not initialized: {e}")
    supabase_client = None
    spaces_client = None
```

**Issue**: Inconsistent error handling, no unified initialization

---

### 4.5 JSON SAVE/LOAD PATTERN - Repeated Across Modules

Every module that needs to persist data re-implements JSON save/load:

```python
# gemini_analyzer.py
with open(analysis_file, 'w') as f:
    json.dump(analysis, f, indent=2)

# ad_evaluator.py
with open(eval_path, 'w') as f:
    json.dump(evaluation, f, indent=2)

# sora_client.py (implicit)
# logger.py
with open(self.progress_log, 'w') as f:
    json.dump(self.progress, f, indent=2)
```

**Instances**: 29 occurrences across 10 modules

**Solution**: Create utility module for persistence

---

### 4.6 API ERROR HANDLING - Inconsistent Patterns

```python
# PATTERN 1: Explicit status checks (sora_client.py:60-68)
if response.status_code != 200:
    print(f"✗ API Error: {response.status_code}")
    print(f"▸ Response body: {response.text[:500]}")
response.raise_for_status()

# PATTERN 2: Try/except wrapper (server.py, various places)
try:
    result = self.client.table('settings').select('*').execute()
except Exception as e:
    print(f"Error fetching setting: {e}")
    return None

# PATTERN 3: Silent failure (spaces_client.py:254-256)
except Exception as e:
    print(f"Error listing session files: {e}")
    return []
```

**Issue**: Inconsistent retry logic, logging, and user feedback

---

### 4.7 LOGGING CALLS - Scattered Across All Modules

Every module has its own logging approach:

```python
# Console-only logging
print(f"✓ Analysis complete: {analysis_path}")

# Structured logging (logger.py)
logger.log(LogLevel.INFO, "Pipeline session started", {...})

# Database logging (server.py)
supabase_client.log_event(session_id, 'info', message, data)

# WebSocket logging (server.py - WebSocketLogger)
socketio.emit('event', {...})
```

**Files with logging**: 15+ files, each with different approach

**Impact**: Hard to track execution flow, inconsistent timestamps/formatting

---

## 5. SETTINGS & CONFIG MANAGEMENT

### Current State (FRAGMENTED)

**Tier 1: Environment Variables**
```python
# config.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 3000))
```

**Tier 2: Static Config Class**
```python
class Config:
    SORA_MODEL = 'sora-2-pro'
    SORA_RESOLUTION = '1792x1024'
    SORA_DURATION = '12'
    AUDIO_ENABLED = True
    AUDIO_MIX = 'cinematic'
    TEXT_FONT_PRIMARY = 'Bebas Neue'
```

**Tier 3: Database (Supabase)**
```python
# settings_manager.py
def get_sora_config(self) -> Dict:
    setting = self.get_setting('sora_config', 'technical_specs')
```

**Tier 4: Hardcoded Defaults in Modules**
```python
# aggression_variants.py
if not all(level in self.presets for level in required_levels):
    self.presets = self._get_default_presets()

# sora_transformer.py
HOOK_SCENARIOS = { # 100+ lines of hardcoded scenarios }
```

**Problem**: 
- Config scattered across 4+ files
- No clear hierarchy
- Updates require changes in multiple places
- Fallback logic unclear

---

## 6. API/SERVER LAYER ORGANIZATION

### Flask Server (server.py)

**Characteristics**:
- Single 777-line file
- 15+ route handlers
- Mixed concerns: API, WebSocket, file upload

**Endpoint Categories**:

| Category | Routes | Lines |
|----------|--------|-------|
| Health/Status | `/api/health`, `/api/sessions` | 50 |
| Cloning Pipeline | `/api/clone`, `/api/preview`, `/api/generate` | 150 |
| File Management | `/api/upload`, `/api/sessions/{id}/videos` | 100 |
| Settings Management | `/api/settings/*` (6 endpoints) | 130 |
| WebSocket Handlers | `@socketio.on(...)` (3 handlers) | 50 |
| Utility Functions | `allowed_file()`, broadcast functions | 30 |

**Issues**:
- Single file is 777 lines - violates SRP
- Mixed async (WebSocket) and sync (HTTP) logic
- WebSocketLogger class defined inline (line 213-248)
- Settings management could be separate blueprint

**Recommendation**: Split into blueprints/modules

---

## 7. PIPELINE STAGE ORCHESTRATION

### Current Flow (ad_cloner.py clone_ad method)

```python
Stage 1: ANALYSIS (Lines 93-141)
├─ Time: 5-10 minutes
├─ Logger: start_stage('analysis')
├─ Output: analysis dict + analysis_path
└─ Error Handling: Raises exception if fails

Stage 1.5: TRANSFORMATION (Lines 143-191)
├─ Condition: Optional (on error, uses original)
├─ Detector: SoraAdTransformer.detect_vertical()
├─ Transformer: SoraAdTransformer.transform_to_sora_structure()
└─ Output: Modified analysis['scene_breakdown']

Stage 2: VARIANTS (Lines 193-236)
├─ Generator: AggressionVariantGenerator.generate_variants()
├─ Filter: Optional filtering by variant_level
└─ Output: List of 4 variant dictionaries

Stage 3: PROMPT COMPOSITION (Lines 238-331)
├─ Builder: SoraPromptBuilder.build_all_scene_prompts()
├─ Validator: PromptValidator.validate_all_prompts()
├─ Logger: Per-scene prompt logging
└─ Output: Dict[variant_level] = [prompts]

Stage 4: GENERATION (Lines 333-396)
├─ Parallel: sora_client.generate_variant_parallel()
├─ Polling: Built into SoraClient
├─ Progress: Tracked per scene
└─ Output: Dict[variant_level] = result

Stage 5: ASSEMBLY (Lines 398-417)
├─ Assembler: VideoAssembler.assemble_variant()
├─ Method: FFmpeg stitching
└─ Output: Dict[variant_level] = final_path

Stage 6: EVALUATION (Lines 419-462)
├─ Evaluator: AdEvaluator.evaluate_generated_ad()
├─ Analysis: Gemini analysis of generated video
└─ Output: Dict[variant_level] = evaluation
```

**Issues**:
- Stage 1.5 is optional/best-effort
- Stage 3 has multiple unused pathways
- Stage 6 fails silently (try/except, lines 456-462)
- No transaction/rollback on partial failure

---

## 8. DETAILED REDUNDANCY FINDINGS

### Summary Table

| Category | Issue | Instances | Files | Severity |
|----------|-------|-----------|-------|----------|
| **Code Duplication** | _normalize_spokesperson() | 2 | 2 | HIGH |
| **Config Scattering** | Same values in 3+ places | 8+ | 4 | HIGH |
| **Prompt Pathways** | 3 unused pathways | 3 | 3 | CRITICAL |
| **Client Initialization** | 3 patterns | 3 | 5 | MEDIUM |
| **JSON Persistence** | Repeated pattern | 29 | 10 | MEDIUM |
| **Error Handling** | 3+ patterns | 15+ | 15+ | MEDIUM |
| **Logging Approaches** | Mixed strategies | 4 | 15+ | HIGH |

---

## 9. CONSOLIDATION OPPORTUNITIES

### Priority 1: CRITICAL (Do First)

#### 1.1 Consolidate Prompt Pathways
**Current State**: 3 unused pathways consuming maintenance
**Action**:
```python
# Create single prompt generation interface
class PromptGenerator:
    def generate(self, analysis, variants) -> Dict[str, List[Dict]]:
        # Single source of truth
        # Could support multiple backends (builder, director, etc.)
        pass

# Usage
gen = PromptGenerator()
variant_prompts = gen.generate(analysis, all_variants)
```
**Impact**: Removes 2 unused modules, clarifies data flow

#### 1.2 Extract Utilities Module
**Create**: `modules/utils.py`
```python
# Shared utilities
def normalize_spokesperson(analysis: Dict) -> Dict:
    """Normalize both list and dict formats"""
    pass

def load_json(path: str) -> Dict:
    """Safe JSON loading with error handling"""
    pass

def save_json(data: Dict, path: str) -> bool:
    """Safe JSON persistence"""
    pass

def handle_api_error(response) -> Dict:
    """Consistent API error handling"""
    pass
```
**Impact**: -20 lines duplication, +1 import per file

---

### Priority 2: HIGH (Do Next)

#### 2.1 Consolidate Configuration
**Action**: Create `ConfigManager` class
```python
class ConfigManager:
    """Unified configuration source"""
    
    def __init__(self):
        self._env_config = self._load_env()
        self._db_config = self._load_from_db()
        self._defaults = self._load_defaults()
    
    def get(self, key: str, section: str = 'core') -> Any:
        # Hierarchy: env → database → defaults
        pass
```

**Files to Update**: 
- Remove hardcoded config from `aggression_variants.py`
- Move `HOOK_SCENARIOS` to database
- Unify `sora_transformer.py`, `aggression_variants.py`, `settings_manager.py`

---

#### 2.2 Unified Client Factory
**Create**: `modules/client_factory.py`
```python
class ClientFactory:
    """Unified client initialization with retry logic"""
    
    @staticmethod
    def get_supabase_client(retry=3) -> Optional[SupabaseClient]:
        pass
    
    @staticmethod
    def get_spaces_client(retry=3) -> Optional[SpacesClient]:
        pass
    
    @staticmethod
    def get_sora_client(...) -> SoraClient:
        pass
```

**Impact**: Consistent error handling across 5+ files

---

#### 2.3 Unified Logging
**Action**: Extend `logger.py` to support multiple backends

```python
class PipelineLogger:
    def __init__(self, session_id=None, backends=None):
        self.backends = backends or ['file', 'console']
        # backend options: file, console, database, websocket
    
    def log(self, level, message, data=None):
        # Route to all backends
        for backend in self.backends:
            self._log_to_backend(backend, level, message, data)
```

---

### Priority 3: MEDIUM (Do Later)

#### 3.1 Split server.py into Blueprints
```
server.py (main, setup)
├─ routes/
│  ├─ clone.py (cloning endpoints)
│  ├─ health.py (health/status)
│  ├─ videos.py (video listing/management)
│  ├─ settings.py (settings CRUD)
│  └─ upload.py (file upload)
└─ websocket.py (WebSocket handlers)
```

#### 3.2 Error Handling Layer
**Create**: `modules/error_handler.py`
```python
class ErrorHandler:
    def handle_api_error(self, error, context) -> Dict:
        pass
    
    def handle_sora_error(self, error) -> Dict:
        pass
```

#### 3.3 Standardize JSON Persistence
**Create**: `modules/persistence.py`
```python
class JSONPersistence:
    @staticmethod
    def save(data: Dict, path: str, mkdir=True) -> bool:
        pass
    
    @staticmethod
    def load(path: str, default=None) -> Dict:
        pass
```

---

## 10. SUMMARY TABLE: BEFORE/AFTER REFACTORING

| Aspect | Before | After | Improvement |
|--------|--------|-------|------------|
| **Duplicate Functions** | 2 | 0 | -100% |
| **Config Sources** | 4+ | 1 | -75% |
| **Prompt Pathways** | 3 | 1 | -67% |
| **Init Patterns** | 3 | 1 | -67% |
| **JSON Implementations** | 29 | 1 | -97% |
| **Error Patterns** | 4+ | 1 | -75% |
| **server.py Lines** | 777 | ~250 | -68% |
| **Module Count** | 16 | 18* | +12% |

*Additional modules: utils.py, config_manager.py, client_factory.py, error_handler.py, persistence.py

---

## 11. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (2-3 days)
1. Create `utils.py` - Move duplicate functions
2. Create `persistence.py` - JSON helpers
3. Create `client_factory.py` - Client initialization
4. Extract `ConfigManager` class

### Phase 2: Integration (3-4 days)
1. Consolidate prompt generation (remove unused modules)
2. Update all modules to use new utilities
3. Implement unified logging backends
4. Update configuration sources

### Phase 3: API Refactoring (2-3 days)
1. Split `server.py` into blueprints
2. Create error handler middleware
3. Add request validation layer

### Phase 4: Testing & Documentation (2-3 days)
1. Unit tests for new utilities
2. Integration tests for refactored pipeline
3. Update README with new architecture

---

## 12. UNUSED MODULES TO DEPRECATE

Based on code analysis, the following modules appear unused in current flow:

1. **`ad_director.py`** - AI Director pathway not called in clone_ad()
2. **`sora_prompt_composer.py`** - Composer pathway not called
3. **`marketing_validator.py`** - Validator called from director (not used)
4. **`conversion_optimizer.py`** - Minimal usage

**Recommendation**: Keep for modularity, but consolidate interfaces

---

## 13. MISSING ABSTRACTION LAYERS

Current architecture is missing:

1. **Pipeline Interface** - No abstract pipeline contract
2. **Module Registry** - No service locator pattern
3. **Configuration Interface** - Config scattered across files
4. **Storage Interface** - Direct JSON file access everywhere
5. **Logging Interface** - Multiple logging backends not abstracted
6. **Error Recovery** - No retry/fallback strategies

---

## CONCLUSION

The soraking repository has **excellent modularization** but suffers from:

1. **Configuration fragmentation** - values defined in 4+ places
2. **Code duplication** - 29 JSON operations, 2 normalize functions
3. **Unused pathways** - 3 prompt generation methods, only 1 active
4. **Inconsistent patterns** - error handling, logging, initialization
5. **Monolithic server file** - 777 lines mixing concerns

**Total Consolidation Potential**: 
- Reduce duplicate code by ~30%
- Eliminate ~100 lines of redundant configuration
- Remove 2-3 unused modules
- Decrease error handling variants from 4+ to 1

**Effort**: 10-15 days for full refactoring with comprehensive testing
