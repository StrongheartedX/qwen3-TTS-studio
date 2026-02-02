#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from podcast import orchestrator as podcast_orchestrator


def progress_callback(step: str, detail: dict | None) -> None:
    if detail is None:
        print(f"[{step}]")
        return

    status = detail.get("status", "")

    if step == "generate_clips" and status == "progress":
        current = detail.get("current", 0)
        total = detail.get("total", 0)
        segment = detail.get("segment", {})
        speaker = segment.get("speaker", "Unknown")
        text_preview = segment.get("text", "")[:40]
        print(f"  [{current}/{total}] {speaker}: {text_preview}...")
    elif status == "started":
        print(f"[{step}] Starting...")
    elif status == "completed":
        if step == "generate_outline":
            outline = detail.get("outline", {})
            segments = outline.get("segments", [])
            print(f"[{step}] Completed - {len(segments)} segments")
        elif step == "generate_transcript":
            transcript = detail.get("transcript", {})
            dialogues = transcript.get("dialogues", [])
            print(f"[{step}] Completed - {len(dialogues)} dialogue lines")
        elif step == "generate_clips":
            print(f"[{step}] Completed - {detail.get('clip_count', 0)} clips generated")
        elif step == "combine_audio":
            print(f"[{step}] Completed - {detail.get('output_path', '')}")
        else:
            print(f"[{step}] Completed")
    elif status == "failed":
        print(f"[{step}] FAILED: {detail.get('error', 'Unknown error')}")
    else:
        print(f"[{step}] {status}")


def main():
    print("=" * 60)
    print("Generating Sample Podcast with 3 Voices")
    print("=" * 60)
    print()

    content_input = {
        "topic": "The Future of AI Assistants: Are They Getting Too Smart?",
        "key_points": [
            "How AI assistants have evolved in the past 5 years",
            "Funny moments when AI gets things hilariously wrong",
            "Will AI assistants replace human interaction?",
        ],
        "briefing": """Create an engaging, conversational podcast with natural banter.
        The host should guide the conversation with energy.
        The expert should provide thoughtful insights with occasional humor.
        The guest should share personal anecdotes and ask curious questions.
        Keep the tone light and entertaining while being informative.""",
        "num_segments": 3,
        "language": "English",
    }

    voice_selections = [
        {"voice_id": "serena", "role": "Host", "type": "preset", "name": "Sarah"},
        {"voice_id": "ryan", "role": "Expert", "type": "preset", "name": "Ryan"},
        {"voice_id": "vivian", "role": "Guest", "type": "preset", "name": "Vivian"},
    ]

    print("Podcast Configuration:")
    print(f"  Topic: {content_input['topic']}")
    print(f"  Segments: {content_input['num_segments']}")
    print(f"  Voices:")
    for v in voice_selections:
        print(f"    - {v['name']} ({v['role']}): {v['voice_id']}")
    print()

    try:
        result = podcast_orchestrator.generate_podcast(
            content_input=content_input,
            voice_selections=voice_selections,
            quality_preset="quick",
            progress_callback=progress_callback,
        )

        print()
        print("=" * 60)
        print("Podcast Generation Complete!")
        print("=" * 60)
        print()
        print("Generated Files:")
        for key, path in result.items():
            print(f"  {key}: {path}")
        print()
        print(f"Final podcast audio: {result.get('combined_audio_path', 'N/A')}")

    except Exception as e:
        print(f"\nError generating podcast: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
