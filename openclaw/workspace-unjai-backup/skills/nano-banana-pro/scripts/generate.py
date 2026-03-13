#!/usr/bin/env python3
"""
Nano Banana Pro - Image Generation Script 🍌
Generates creative images with playful nano-banana aesthetics!
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

# Style modifiers
STYLE_MODIFIERS = {
    "cute": "kawaii style, soft pastel colors, adorable, chibi-like proportions, big expressive eyes, charming and sweet",
    "miniature": "tiny world, macro photography style, miniature figures, tilt-shift effect, intricate small details",
    "playful": "fun, whimsical, bright cheerful colors, energetic vibe, cartoon-like, joyful and lively",
    "professional": "sleek, modern, clean lines, subtle elegance, polished look with a tiny hint of playfulness",
    "banana": "yellow color accents, curved shapes, tropical vibes, fruity freshness, monkey-approved aesthetics"
}

def generate_image(prompt: str, style: str = "playful", size: str = "1024x1024", count: int = 1):
    """Generate images using OpenAI's DALL-E 3."""
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Add style modifier
    style_modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["playful"])
    full_prompt = f"{prompt}, {style_modifier}, high quality, detailed"
    
    print(f"🍌 Nano Banana Pro generating image...")
    print(f"📝 Prompt: {prompt}")
    print(f"🎨 Style: {style}")
    print(f"📐 Size: {size}")
    print("-" * 50)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    generated_files = []
    
    for i in range(count):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size=size,
                quality="hd",
                n=1
            )
            
            # Download image
            image_url = response.data[0].url
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nano_banana_{style}_{timestamp}_{i+1}.png"
            filepath = output_dir / filename
            
            import requests
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(image_response.content)
            
            generated_files.append(filepath)
            print(f"✅ Saved: {filepath}")
            
        except Exception as e:
            print(f"❌ Error generating image {i+1}: {e}")
    
    # Save metadata
    metadata = {
        "prompt": prompt,
        "style": style,
        "full_prompt": full_prompt,
        "size": size,
        "count": count,
        "generated_at": datetime.now().isoformat(),
        "files": [str(f) for f in generated_files]
    }
    
    meta_file = output_dir / f"nano_banana_{timestamp}_metadata.json"
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("-" * 50)
    print(f"🎉 Generated {len(generated_files)} image(s)!")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print("🍌 Nano Banana Pro says: Have a great day!")
    
    return generated_files

def main():
    parser = argparse.ArgumentParser(
        description="🍌 Nano Banana Pro - Generate fun images with banana aesthetics!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate.py --prompt "cute cat" --style cute
  python3 generate.py --prompt "business portrait" --style professional
  python3 generate.py --prompt "fantasy castle" --style miniature --count 2
        """
    )
    
    parser.add_argument("--prompt", "-p", required=True, help="Image description")
    parser.add_argument("--style", "-s", 
                       choices=["cute", "miniature", "playful", "professional", "banana"],
                       default="playful",
                       help="Image style (default: playful)")
    parser.add_argument("--size", 
                       choices=["1024x1024", "1792x1024", "1024x1792"],
                       default="1024x1024",
                       help="Image size (default: 1024x1024)")
    parser.add_argument("--count", "-c", type=int, default=1,
                       help="Number of images to generate (default: 1)")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.style, args.size, args.count)

if __name__ == "__main__":
    main()
