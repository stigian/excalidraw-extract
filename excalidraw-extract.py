#!/usr/bin/env python3
# (c) 2025 Stigian Consulting

import argparse
import struct
import zlib
import base64
import json
from pathlib import Path

def read_chunks(png_bytes):
    offset = 8  # Skip the PNG signature
    while offset < len(png_bytes):
        if offset + 8 > len(png_bytes):
            break
        length = struct.unpack(">I", png_bytes[offset:offset+4])[0]
        type_code = png_bytes[offset+4:offset+8].decode('latin1')
        data = png_bytes[offset+8:offset+8+length]
        yield type_code, data
        offset += 8 + length + 4  # Advance to next chunk

def scan_for_excalidraw_scene(data_bytes):
    try:
        text = data_bytes.decode("latin1")
        if text.startswith("application/vnd.excalidraw+json\x00"):
            json_start = text.find('\x00') + 1
            scene_meta = json.loads(text[json_start:])
            encoded = scene_meta.get("encoded")
            if not encoded:
                return None
            decompressed = zlib.decompress(encoded.encode("latin1")).decode("utf-8")
            scene = json.loads(decompressed)
            return scene
    except Exception:
        pass
    return None

def scan_for_svg(data_bytes):
    try:
        decoded = data_bytes.decode("utf-8")
        if "<svg" in decoded and "</svg>" in decoded:
            start = decoded.find("<svg")
            end = decoded.rfind("</svg>") + len("</svg>")
            return decoded[start:end]
    except Exception:
        pass
    return None

def detect_and_extract(png_path, extract=False, output_path=None):
    with open(png_path, "rb") as f:
        content = f.read()
    if not content.startswith(b'\x89PNG\r\n\x1a\n'):
        print("❌ Not a valid PNG file.")
        return False

    found = False
    for chunk_type, data in read_chunks(content):
        # Check for Excalidraw scene first
        scene = scan_for_excalidraw_scene(data)
        if scene:
            print(f"✅ Found embedded Excalidraw scene in chunk '{chunk_type}'")
            if extract:
                output_file = output_path or (Path(png_path).stem + ".excalidraw.json")
                with open(output_file, "w", encoding="utf-8") as out:
                    json.dump(scene, out, indent=2)
                print(f"📝 Scene extracted to: {output_file}")
            found = True
            break  # Excalidraw embeds usually only occur once

        # Fallback: check for SVG (optional)
        svg = scan_for_svg(data)
        if svg:
            print(f"✅ Found embedded SVG in chunk '{chunk_type}'")
            if extract:
                output_file = output_path or (Path(png_path).stem + ".embedded.svg")
                with open(output_file, "w", encoding="utf-8") as out:
                    out.write(svg)
                print(f"📝 SVG extracted to: {output_file}")
            found = True
            break

    if not found:
        print("❌ No embedded Excalidraw scene or SVG found.")
    return found

def main():
    parser = argparse.ArgumentParser(description="Detect or extract embedded Excalidraw scene or SVG from PNG.")
    parser.add_argument("png_file", help="Path to the PNG file")
    parser.add_argument("--extract", action="store_true", help="Extract the embedded scene or SVG")
    parser.add_argument("--output", help="Custom output path")
    args = parser.parse_args()

    detect_and_extract(args.png_file, extract=args.extract, output_path=args.output)

if __name__ == "__main__":
    main()
