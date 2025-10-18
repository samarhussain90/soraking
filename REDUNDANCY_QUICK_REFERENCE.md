# SORAKING - QUICK REDUNDANCY REFERENCE

## Critical Redundancies Found (At-a-Glance)

### 1. DUPLICATE FUNCTION: `_normalize_spokesperson()`

**Files**: `ad_cloner.py` + `sora_transformer.py`
**Lines**: 20 lines duplicated
**Calls**: 3 call sites across codebase

```python
# LOCATION 1: ad_cloner.py:52-72
# LOCATION 2: sora_transformer.py (~similar)
```

**Action**: Extract to `modules/utils.py` → immediate 20-line reduction

---

### 2. CONFIGURATION FRAGMENTATION

**Problem**: Same config values defined in 4+ files

| Value | config.py | settings_manager.py | aggression_variants.py | sora_transformer.py |
|-------|-----------|-------------------|--------------------|--------------------|
| SORA_MODEL | ✓ | - | - | - |
| SORA_RESOLUTION | ✓ | ✓ (different) | - | - |
| AUDIO_MIX | ✓ | ✓ (different) | - | - |
| HOOK_SCENARIOS | - | - | - | ✓ (100+ lines) |
| Aggression Presets | - | ✓ | ✓ | - |

**Files**: config.py, settings_manager.py, aggression_variants.py, sora_transformer.py
**Redundant Lines**: ~200 lines spread across 4 files

**Action**: Create `ConfigManager` class with hierarchy: ENV → DB → Defaults

---

### 3. JSON PERSISTENCE - 29 Repeated Implementations

**Pattern**: `with open(file) as f: json.dump(data, f)` repeated everywhere

**Files with JSON operations** (29 total):
- gemini_analyzer.py: 3
- logger.py: 5
- ad_evaluator.py: 2
- sora_transformer.py: 5
- sora_client.py: 2
- ad_director.py: 4
- marketing_validator.py: 3

**Action**: Create `modules/persistence.py`

```python
def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path) as f:
        return json.load(f)
```

**Impact**: -50 lines of boilerplate, +1 unified implementation

---

### 4. PROMPT GENERATION - 3 UNUSED PATHWAYS

**Current Active**: `SoraPromptBuilder.build_all_scene_prompts()` (ad_cloner.py:245)

**Unused Pathways**:
1. `AdDirector.generate_scene_structure()` (ad_director.py)
2. `SoraPromptComposer.compose_from_director_scenes()` (sora_prompt_composer.py)
3. `MarketingValidator.validate_and_refine()` (used by director only)

**Files**: ad_director.py, sora_prompt_composer.py, marketing_validator.py
**Lines**: ~600 of unused code

**Action**: Create `PromptGenerator` interface, deprecate 2 modules, consolidate to 1

```python
# New unified interface
class PromptGenerator:
    def generate(self, analysis, variants, method='builder'):
        if method == 'builder':
            return SoraPromptBuilder().build_all_scene_prompts(...)
        elif method == 'director':
            return AdDirector().generate_scene_structure(...)
```

---

### 5. CLIENT INITIALIZATION - 3 Patterns

**Pattern 1: Singleton with global** (logger.py, settings_manager.py)
```python
_current_logger = None
def get_logger(session_id=None):
    global _current_logger
    if _current_logger is None or session_id:
        _current_logger = PipelineLogger(session_id)
    return _current_logger
```

**Pattern 2: Direct instantiation** (server.py, ad_cloner.py)
```python
supabase_client = SupabaseClient()
spaces_client = SpacesClient()
```

**Pattern 3: Try/except with fallback** (server.py:26-35)
```python
try:
    supabase_client = SupabaseClient()
except Exception:
    supabase_client = None
```

**Files**: 5+ files with inconsistent patterns
**Action**: Create `ClientFactory` with unified error handling

---

### 6. ERROR HANDLING - 4+ Patterns

**Pattern 1**: Explicit status checks
```python
if response.status_code != 200:
    raise Exception(response.text)
```

**Pattern 2**: Try/except silence
```python
try:
    result = api_call()
except Exception as e:
    return None  # Silent fail
```

**Pattern 3**: Print only
```python
except Exception as e:
    print(f"Error: {e}")
    # No logging, no recovery
```

**Pattern 4**: No error handling
```python
# Many calls have no error handling
response.raise_for_status()
```

**Files**: 15+ files with mixed approaches
**Action**: Create `ErrorHandler` with consistent logging + retry

---

### 7. LOGGING APPROACHES - 4 Different Methods

**Method 1**: Print statements (15+ files)
```python
print(f"✓ Analysis complete: {analysis_path}")
```

**Method 2**: Structured logging (logger.py)
```python
logger.log(LogLevel.INFO, "message", {data})
```

**Method 3**: Database logging (server.py)
```python
supabase_client.log_event(session_id, 'info', message, data)
```

**Method 4**: WebSocket logging (server.py)
```python
socketio.emit('event', {...})
```

**Impact**: Hard to track flow, inconsistent timestamps
**Action**: Extend `PipelineLogger` to support multiple backends

---

## REDUNDANCY SUMMARY TABLE

| Issue | Type | Severity | Files | Lines | Fix Effort |
|-------|------|----------|-------|-------|-----------|
| _normalize_spokesperson() | Code Dup | HIGH | 2 | 20 | 1 hour |
| Config Fragmentation | Config | CRITICAL | 4 | 200 | 4 hours |
| JSON Persistence | Pattern | MEDIUM | 10 | 50* | 2 hours |
| Prompt Pathways | Logic | CRITICAL | 3 | 600 | 8 hours |
| Client Init | Pattern | MEDIUM | 5 | 30 | 2 hours |
| Error Handling | Pattern | MEDIUM | 15+ | 100 | 6 hours |
| Logging | Pattern | HIGH | 15+ | 200 | 8 hours |

*Actual code, not counting duplicate boilerplate

---

## QUICK FIX CHECKLIST

### Day 1 (Foundation)
- [ ] Create `modules/utils.py` with `normalize_spokesperson()`
- [ ] Create `modules/persistence.py` with JSON helpers
- [ ] Update all modules to use utils
- [ ] Remove duplicate functions

### Day 2 (Consolidation)
- [ ] Create `ConfigManager` class
- [ ] Migrate config values to ConfigManager
- [ ] Move HOOK_SCENARIOS to database
- [ ] Update all config references

### Day 3 (Infrastructure)
- [ ] Create `ClientFactory` class
- [ ] Consolidate initialization patterns
- [ ] Create unified error handler
- [ ] Extend logger for multiple backends

### Day 4 (Cleanup)
- [ ] Consolidate prompt generation (1 interface, 3 implementations)
- [ ] Deprecate unused pathways
- [ ] Split server.py into blueprints
- [ ] Add comprehensive tests

---

## PRIORITY ORDER

### Immediate (Do Now)
1. Extract `_normalize_spokesperson()` to utils.py
2. Create `persistence.py` for JSON operations
3. Consolidate 3 prompt pathways to 1 interface

### High (Do This Week)
1. Consolidate configuration across 4 files
2. Create ClientFactory for consistent initialization
3. Standardize error handling

### Medium (Do Next Week)
1. Extend logger for multiple backends
2. Split server.py into blueprints
3. Add comprehensive tests

---

## CONSOLIDATION IMPACT

### Code Reduction
- Eliminate 2 duplicate functions (-20 lines)
- Consolidate JSON patterns (-50 lines)
- Merge 3 prompt pathways (-600 lines)
- Reduce config duplication (-200 lines)
- **Total: -870 lines of duplicate/scattered code**

### Maintainability Improvements
- Configuration: 4 sources → 1 (75% reduction)
- Error handling: 4+ patterns → 1 (75% reduction)
- Logging: 4 approaches → 1 unified (100% reduction)
- JSON operations: 29 implementations → 1 (97% reduction)

### Testing Benefits
- 1 error handler to test instead of 4+
- 1 config source to mock instead of 4
- 1 JSON persistence layer to test instead of 29

---

## FILES TO CREATE/MODIFY

### Create (New Files)
1. `modules/utils.py` - Utility functions
2. `modules/persistence.py` - JSON helpers
3. `modules/client_factory.py` - Client initialization
4. `modules/error_handler.py` - Error handling
5. `modules/config_manager.py` - Configuration

### Modify (Existing Files)
1. `config.py` - Remove redundant values
2. `ad_cloner.py` - Remove duplicate functions
3. `server.py` - Split into blueprints (optional)
4. `logger.py` - Add backend support
5. All 16 modules - Use new utilities

### Deprecate (Can Remove)
1. `ad_director.py` (move to utilities/examples)
2. `sora_prompt_composer.py` (move to utilities/examples)
3. `marketing_validator.py` (conditional use)

---

## VALIDATION CHECKLIST

After refactoring:
- [ ] All tests pass
- [ ] Configuration loads from single source
- [ ] No duplicate functions
- [ ] All JSON operations use persistence layer
- [ ] All error handling consistent
- [ ] All logging goes through logger
- [ ] Server follows modular structure
- [ ] 3 prompt pathways consolidated to 1
- [ ] Code coverage >80%
- [ ] Documentation updated

