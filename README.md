# excalidraw-extract
Python CLI tool to detect and extract Excalidraw embedded scene files from PNG exports

- Detects and extracts Excalidraw scenes embedded in PNGs via the tEXt chunk.
- Supports --extract to write the embedded scene to .excalidraw.json.
- Supports optional detection of <svg> blocks if they exist in other chunks.

