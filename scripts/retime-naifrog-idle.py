#!/usr/bin/env python3
"""Losslessly reorder the approved v1.3.1 idle frames into a ping-pong loop.

Requires Pillow. No generation, interpolation, matting, cropping or scaling.
The source's first 24 frames are the original glance; its remaining nine
frames belong to the old dissolve/return and are deliberately excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

SOURCE_SHA256 = "94b23d27065ace8181f023c979b66334f66b9ca3b9197c2d00eacf393922c4c3"


def visible_equal(left, right):
    if left.getchannel("A").tobytes() != right.getchannel("A").tobytes():
        return False
    # Invisible RGB may be discarded by WebP. Compare every visible pixel.
    mask = left.getchannel("A").point(lambda value: 255 if value else 0)
    difference = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return ImageChops.multiply(difference, Image.merge("RGB", (mask, mask, mask))).getbbox() is None


def retime(source, output):
    source, output = Path(source), Path(output)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA256, "Expected the approved 1.3.1 source"
    image = Image.open(source)
    assert image.size == (640, 640) and image.n_frames == 33
    source_frames = []
    for frame in ImageSequence.Iterator(image):
        source_frames.append(frame.convert("RGBA").copy())
        if len(source_frames) == 24:
            break
    # Do not repeat either turning point: ...22,23,22... and ...1,0,1...
    order = list(range(24)) + list(range(22, 0, -1))
    frames = [source_frames[index] for index in order]
    durations = [round((index + 1) * 2000 / len(order)) - round(index * 2000 / len(order)) for index in range(len(order))]
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    frames[0].save(temporary, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, lossless=True, quality=75, method=3, exact=True)
    decoded = Image.open(temporary)
    observed = []
    for frame in ImageSequence.Iterator(decoded):
        observed.append((frame.convert("RGBA").copy(), frame.info["duration"]))
    assert len(observed) == len(order), "Unexpected frame merging"
    for (frame, duration), expected, expected_duration in zip(observed, frames, durations):
        assert visible_equal(frame, expected), "Visible source pixels changed"
        assert duration == expected_duration
    assert sum(duration for _, duration in observed) == 2000
    assert decoded.info["loop"] == 0
    assert all(abs(order[(index + 1) % len(order)] - value) == 1 for index, value in enumerate(order))
    decoded.close()
    temporary.replace(output)
    return {
        "sourceVersion": "1.3.1", "sourceSha256": SOURCE_SHA256,
        "outputSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "sourceFrames": 24, "outputFrames": len(order), "durationMs": 2000,
        "frameOrder": order, "frameDurationsMs": durations,
        "sourcePlayback": "forward then reverse; endpoints are not duplicated",
        "returnDissolveMs": 0, "restMs": 0, "newGeneration": False,
        "lossless": True, "visiblePixelsPreserved": True,
        "allStepsIncludingWrapAreAdjacentSourceFrames": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = retime(args.input, args.output)
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text)
