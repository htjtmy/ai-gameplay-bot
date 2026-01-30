#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate SRT from English to Simplified Chinese using googletrans.
"""

import math
from pathlib import Path
from typing import List, Tuple

from googletrans import Translator


def parse_srt(content: str) -> List[Tuple[int, str, List[str]]]:
    """Parse SRT content into a list of (index, timestamp, lines)."""
    blocks = content.strip().split("\n\n")
    subtitles: List[Tuple[int, str, List[str]]] = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0])
        except ValueError:
            continue
        timestamp = lines[1]
        text_lines = lines[2:]
        subtitles.append((idx, timestamp, text_lines))
    return subtitles


def write_srt(path: Path, subtitles: List[Tuple[int, str, List[str]]]) -> None:
    """Write subtitles back to SRT format."""
    with path.open("w", encoding="utf-8") as f:
        for i, (idx, timestamp, lines) in enumerate(subtitles):
            f.write(f"{idx}\n")
            f.write(f"{timestamp}\n")
            for line in lines:
                f.write(f"{line}\n")
            if i < len(subtitles) - 1:
                f.write("\n")


def batch_translate(texts: List[str], batch_size: int = 20) -> List[str]:
    """Translate list of texts in batches with fallbacks."""
    translator = Translator()
    results: List[str] = []
    total = len(texts)
    batches = math.ceil(total / batch_size)

    for i in range(batches):
        chunk = texts[i * batch_size : (i + 1) * batch_size]
        try:
            translated = translator.translate(chunk, src="en", dest="zh-cn")
            if not isinstance(translated, list):
                translated = [translated]
            results.extend([t.text for t in translated])
            continue
        except Exception:
            # Fallback to single-item translation for this chunk
            pass

        for text in chunk:
            try:
                t = translator.translate(text, src="en", dest="zh-cn")
                results.append(t.text)
            except Exception:
                results.append(text)  # keep original if translation fails

    return results


def main() -> None:
    input_path = Path(r"d:\\Users\\Source\\Ai-Gameplay-Bot\\logs\\en.srt")
    output_path = Path(r"d:\\Users\\Source\\Ai-Gameplay-Bot\\logs\\zh-cn.srt")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    content = input_path.read_text(encoding="utf-8-sig")
    subtitles = parse_srt(content)
    print(f"Read {len(subtitles)} subtitle blocks")

    # Prepare texts for translation (join multi-line into one sentence)
    texts = [" ".join(lines) for _, _, lines in subtitles]

    print("Translating...")
    translated_texts = batch_translate(texts, batch_size=40)

    # Rebuild subtitles with translated text (single line per block)
    translated_subs: List[Tuple[int, str, List[str]]] = []
    for (idx, timestamp, _), zh in zip(subtitles, translated_texts):
        translated_subs.append((idx, timestamp, [zh]))

    write_srt(output_path, translated_subs)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
