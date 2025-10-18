"""
Sora Prompt Composer (AI-Driven)
Converts AI Director scenes into Sora 2 Pro prompts
"""
from typing import Dict, List


class SoraPromptComposer:
    """Converts AI-generated scene specs into Sora prompts"""
    
    def compose_from_director_scenes(self, director_scenes: List[Dict]) -> List[Dict]:
        """
        Convert AI Director scenes to Sora prompts
        
        Args:
            director_scenes: Scene specs from AdDirector
            
        Returns:
            List of prompt dictionaries ready for Sora
        """
        sora_prompts = []
        
        for scene in director_scenes:
            prompt_text = self._build_scene_prompt(scene)
            
            sora_prompts.append({
                'scene_number': scene['scene_number'],
                'timestamp': scene['timestamp'],
                'scene_type': scene.get('scene_type', 'character'),
                'purpose': scene.get('purpose', ''),
                'prompt': prompt_text,
                'has_audio': bool(scene.get('audio')),
                'has_text': bool(scene.get('text_overlays')),
                'text_count': len(scene.get('text_overlays', []))
            })
        
        return sora_prompts
    
    def _build_scene_prompt(self, scene: Dict) -> str:
        """Build complete Sora prompt from scene spec"""
        parts = []
        
        # 1. VISUAL LAYER (shot progression)
        visual_layer = self._format_visual_layer(scene.get('visual', {}))
        if visual_layer:
            parts.append(visual_layer)
        
        # 2. AUDIO LAYER (voiceover + music + SFX)
        audio_layer = self._format_audio_layer(scene.get('audio', {}))
        if audio_layer:
            parts.append(f"\nAUDIO: {audio_layer}")
        
        # 3. TEXT OVERLAYS (with timing and style)
        text_layer = self._format_text_layer(scene.get('text_overlays', []))
        if text_layer:
            parts.append(f"\nTEXT OVERLAYS: {text_layer}")
        
        # 4. TECHNICAL SPECS
        tech_layer = self._format_technical_layer(scene.get('visual', {}))
        parts.append(f"\n{tech_layer}")
        
        return ''.join(parts)
    
    def _format_visual_layer(self, visual: Dict) -> str:
        """Format shot progression for Sora"""
        shot_progression = visual.get('shot_progression', [])
        if not shot_progression:
            return ""
        
        shots = []
        for shot in shot_progression:
            time = shot.get('time', '00:00-00:03')
            shot_type = shot.get('shot_type', 'medium shot').upper()
            subject = shot.get('subject', 'subject')
            camera_move = shot.get('camera_move', 'static')
            lighting = shot.get('lighting', 'natural')
            focus = shot.get('focus', 'sharp')
            
            shot_desc = f"[{time}] {shot_type}: {subject}. "
            
            if camera_move != 'static':
                shot_desc += f"{camera_move.capitalize()} camera. "
            
            shot_desc += f"{lighting.capitalize()} lighting. {focus.capitalize()} focus."
            shots.append(shot_desc)
        
        return '\n'.join(shots)
    
    def _format_audio_layer(self, audio: Dict) -> str:
        """Format audio specs for Sora"""
        audio_parts = []
        
        # Voiceover
        vo = audio.get('voiceover', {})
        if vo:
            script = vo.get('script', '')
            tone = vo.get('tone', 'conversational')
            pace = vo.get('pace', 'medium')
            emotion = vo.get('emotion', 'neutral')
            
            audio_parts.append(
                f"{tone} voice, {pace} pace, {emotion} emotion. "
                f"Says: \"{script}\""
            )
        
        # Music
        music = audio.get('music', {})
        if music:
            genre = music.get('genre', 'background music')
            bpm = music.get('bpm', 120)
            intensity = music.get('intensity', 'steady')
            key_moments = music.get('key_moments', [])
            
            music_desc = f"Background music: {genre}, {bpm} BPM, {intensity}"
            if key_moments:
                music_desc += f". {', '.join(key_moments)}"
            audio_parts.append(music_desc)
        
        # Sound Effects
        sfx = audio.get('sound_effects', [])
        if sfx:
            sfx_desc = ". ".join([
                f"Sound effect at {s.get('time')}: {s.get('effect')}"
                for s in sfx
            ])
            audio_parts.append(sfx_desc)
        
        return '. '.join(audio_parts) + '.'
    
    def _format_text_layer(self, text_overlays: List[Dict]) -> str:
        """Format text overlays for Sora"""
        if not text_overlays:
            return ""
        
        text_specs = []
        for overlay in text_overlays:
            text = overlay.get('text', '')
            start = overlay.get('start', '0:00')
            end = overlay.get('end', '0:03')
            position = overlay.get('position', 'center')
            font = overlay.get('font', 'Bebas Neue')
            size = overlay.get('size', '120pt')
            color = overlay.get('color', 'white')
            animation = overlay.get('animation', 'fade in')
            outline = overlay.get('outline', 'none')
            
            outline_text = f" with {outline} outline" if outline != 'none' else ""
            
            spec = (
                f'At {start}, {animation}: "{text}" '
                f'({font}, {size}, {color}{outline_text}). '
                f'Fades out at {end}'
            )
            text_specs.append(spec)
        
        return '. '.join(text_specs) + '.'
    
    def _format_technical_layer(self, visual: Dict) -> str:
        """Format technical specs for Sora"""
        color_grade = visual.get('color_grade', 'cinematic')
        energy = visual.get('energy_level', 'engaging')
        
        return (
            f"TECHNICAL: 4K resolution, 1792x1024, "
            f"{energy} style, {color_grade} grade, cinematic audio mix."
        )
