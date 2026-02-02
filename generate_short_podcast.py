#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from podcast.models import Dialogue, Speaker, SpeakerProfile, Transcript
from audio import batch as batch_processor
from audio import combiner as audio_combiner
from storage import history as storage


def main():
    print("=" * 60)
    print("Generating Short Sample Podcast with 3 Voices")
    print("=" * 60)
    print()

    speakers = [
        Speaker(name="Sarah", voice_id="serena", role="Host", type="preset"),
        Speaker(name="Ryan", voice_id="ryan", role="Expert", type="preset"),
        Speaker(name="Vivian", voice_id="vivian", role="Guest", type="preset"),
    ]
    speaker_profile = SpeakerProfile(speakers=speakers)

    dialogues = [
        Dialogue(
            speaker="Sarah",
            text="Welcome to the AI Talk show! Today we're diving deep into the future of artificial intelligence and how it's reshaping our daily lives. I'm Sarah, your host.",
        ),
        Dialogue(
            speaker="Ryan",
            text="Thanks for having me, Sarah. It's a fascinating topic that I'm passionate about. The evolution of AI in just the past few years has been nothing short of remarkable.",
        ),
        Dialogue(
            speaker="Vivian",
            text="I'm so excited to be here! As someone who uses AI tools every single day, I've definitely noticed how much smarter and more intuitive they've become.",
        ),
        Dialogue(
            speaker="Sarah",
            text="Ryan, from a technical perspective, what's the biggest breakthrough you've seen in AI assistants over the past year?",
        ),
        Dialogue(
            speaker="Ryan",
            text="The contextual understanding has improved dramatically. Modern AI systems can now remember what you said earlier in a conversation and follow complex multi-turn dialogues with remarkable accuracy.",
        ),
        Dialogue(
            speaker="Vivian",
            text="That's exactly what I've experienced! My AI assistant remembers my preferences, anticipates what I need, and sometimes even suggests things before I ask for them.",
        ),
        Dialogue(
            speaker="Ryan",
            text="What's interesting is that this capability comes from advances in transformer architectures and attention mechanisms. The models are getting better at understanding context and maintaining coherence.",
        ),
        Dialogue(
            speaker="Sarah",
            text="That's both impressive and thought-provoking. Thank you Ryan and Vivian for sharing these incredible insights with us today on AI Talk!",
        ),
    ]

    transcript = Transcript(dialogues=dialogues)

    print(f"Created transcript with {len(dialogues)} dialogues")
    print(f"Speakers: {', '.join(s.name for s in speakers)}")
    print()

    tts_params = {
        "model_name": "1.7B-CustomVoice",
        "temperature": 0.5,
        "top_k": 30,
        "top_p": 0.9,
        "repetition_penalty": 1.0,
        "max_new_tokens": 768,
        "subtalker_temperature": 0.5,
        "subtalker_top_k": 30,
        "subtalker_top_p": 0.9,
        "language": "en",
        "instruct": None,
    }

    downloads_dir = Path.home() / "Downloads"
    podcast_dir = downloads_dir / "qwen3_podcast_8segments"
    podcast_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = podcast_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {podcast_dir}")
    print()

    def progress_callback(current: int, total: int, segment_info: dict) -> None:
        status = segment_info.get("status", "")
        speaker = segment_info.get("speaker", "")
        text = segment_info.get("text", "")[:40]
        if status == "success":
            print(f"  [{current}/{total}] {speaker}: {text}... Done!")
        elif status == "error":
            print(
                f"  [{current}/{total}] {speaker}: FAILED - {segment_info.get('error', '')}"
            )
        else:
            print(f"  [{current}/{total}] {speaker}: {text}...")

    print("Generating audio clips...")
    try:
        clip_paths = batch_processor.generate_all_clips(
            transcript=transcript,
            speaker_profile=speaker_profile,
            params=tts_params,
            clips_dir=clips_dir,
            progress_callback=progress_callback,
        )

        print()
        print(f"Generated {len(clip_paths)} clips")
        print()

        print("Combining audio clips...")
        output_path = podcast_dir / "final_podcast.mp3"
        combined_path = audio_combiner.combine_audio_clips(
            clips_dir=clips_dir,
            output_path=output_path,
        )

        print()
        print("=" * 60)
        print("Podcast Generation Complete!")
        print("=" * 60)
        print()
        print(f"Final podcast: {combined_path}")
        print(f"Clips directory: {clips_dir}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
