#!/usr/bin/env python3
"""Losslessly retime the approved glance: forward, hold, reverse, normal rest.

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
    # Start with motion. Hold the glance for exactly two seconds, return to
    # source frame zero, then give the neutral pose two seconds to rest.
    # The identical neutral frames across the wrap extend that intentional
    # rest without a visual cut; the glance turning point appears only once.
    order = list(range(24)) + list(range(22, -1, -1))
    frames = [source_frames[index] for index in order]
    def span(count, duration):
        return [round((index + 1) * duration / count) - round(index * duration / count) for index in range(count)]
    durations = span(23, 1000) + [2000] + span(22, 1000) + [2000]
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
    assert sum(duration for _, duration in observed) == 6000
    assert observed[23][1] == 2000 and observed[-1][1] == 2000
    assert visible_equal(observed[23][0], source_frames[-1])
    assert visible_equal(observed[-1][0], source_frames[0])
    assert decoded.info["loop"] == 0
    assert all(abs(right - left) == 1 for left, right in zip(order, order[1:]))
    assert order[-1] == order[0] == 0
    decoded.close()
    temporary.replace(output)
    return {
        "sourceVersion": "1.3.1", "sourceSha256": SOURCE_SHA256,
        "outputSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "sourceFrames": 24, "outputFrames": len(order), "durationMs": 6000,
        "frameOrder": order, "frameDurationsMs": durations,
        "sourcePlayback": "forward 1s, glance hold 2s, reverse 1s, normal pose rest 2s",
        "phases": [
            {"name": "forward", "startMs": 0, "durationMs": 1000},
            {"name": "glance-hold", "startMs": 1000, "durationMs": 2000, "sourceFrame": 23},
            {"name": "reverse", "startMs": 3000, "durationMs": 1000},
            {"name": "normal-rest", "startMs": 4000, "durationMs": 2000, "sourceFrame": 0},
        ],
        "returnDissolveMs": 0, "restMs": 2000, "glanceHoldMs": 2000, "newGeneration": False,
        "lossless": True, "visiblePixelsPreserved": True,
        "motionStepsAreAdjacentSourceFrames": True,
        "wrapUsesIdenticalNormalPose": True,
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
