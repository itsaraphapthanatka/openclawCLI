---
name: nano-banana-pro
description: Generate fun and creative images with a playful "nano banana" style. Use when the user wants to create images with cute, miniature, or banana-themed aesthetics, or when they specifically mention "nano banana" or similar terms.
---

# Nano Banana Pro 🍌

A fun image generation skill with a playful nano-banana twist!

## Overview

This skill generates creative images using OpenAI's image generation API with a distinctive "nano banana" aesthetic - think cute, miniature, playful, and always with a touch of banana charm! 🐵

## Usage

### Generate an Image

```bash
python3 {baseDir}/scripts/generate.py --prompt "your prompt here"
```

### Options

- `--prompt` : Image description (required)
- `--style` : Style modifier - "cute", "miniature", "playful", "professional" (default: playful)
- `--count` : Number of images (1-4, default: 1)
- `--size` : Image size - "1024x1024", "1792x1024", "1024x1792" (default: 1024x1024)

### Examples

```bash
# Cute nano banana style
python3 {baseDir}/scripts/generate.py --prompt "business woman in white suit" --style cute

# Miniature style
python3 {baseDir}/scripts/generate.py --prompt "city skyline" --style miniature --count 2

# Professional with banana touch
python3 {baseDir}/scripts/generate.py --prompt "office meeting" --style professional
```

## Style Modifiers

The skill automatically adds style modifiers based on the selected style:

- **cute**: "kawaii style, soft colors, adorable, chibi-like proportions"
- **miniature**: "tiny world, macro photography style, miniature figures, tilt-shift effect"
- **playful**: "fun, whimsical, bright colors, energetic, cartoon-like"
- **professional**: "sleek, modern, clean lines, subtle banana accent"

## Output

Images are saved to `output/` directory with timestamps and style tags in filenames.

## Requirements

- `OPENAI_API_KEY` environment variable must be set
- Python 3.8+
- Dependencies: openai, requests
