# Archived Unused Modules

This directory contains modules that were part of the initial pipeline design but are no longer used in the active codebase.

## Archived on: 2025-01-18

## Modules

### 1. `ad_director.py` (~300 lines)
- **Purpose**: AI-driven scene generation using OpenAI
- **Why Archived**: Redundant with SoraPromptBuilder
- **Status**: Alternative prompt generation pathway, not used in main flow
- **Can Be Restored**: Yes, if needed for A/B testing different prompt strategies

### 2. `sora_prompt_composer.py` (~170 lines)
- **Purpose**: Convert AI-generated scenes to Sora prompts
- **Why Archived**: SoraPromptBuilder handles this directly
- **Status**: Intermediate layer that's no longer needed
- **Can Be Restored**: Yes, though SoraPromptBuilder is preferred

### 3. `marketing_validator.py`
- **Purpose**: Validate and optimize prompts for conversion
- **Why Archived**: Only used by ad_director.py, which is also archived
- **Status**: Partial implementation, not in main pipeline
- **Can Be Restored**: Yes, could be integrated with prompt validation

## Active Prompt Generation

The **active** prompt generation pathway is:
1. `GeminiVideoAnalyzer` - Analyze original video
2. `SoraAdTransformer` - Transform with extreme hooks
3. `AggressionVariantGenerator` - Generate variants
4. **`SoraPromptBuilder`** - Build final Sora prompts (ACTIVE)
5. `PromptValidator` - Validate prompts
6. `SoraClient` - Generate videos

## Restoration Instructions

If you need to restore any of these modules:

1. Move the module back to `modules/` directory
2. Add the import to `ad_cloner.py`
3. Initialize in `AdCloner.__init__()`
4. Integrate into the pipeline flow

## Code Reduction

Archiving these modules reduced the active codebase by:
- **~600 lines** of unused code
- **3 unused class instantiations** in AdCloner
- **3 unused imports** in ad_cloner.py

This improves:
- Code maintainability
- Startup performance
- Debugging clarity
