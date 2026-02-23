"""
Quick test: Analyze electrical drawing with Claude Vision
Run this to see if Claude can extract panels/circuits from a drawing
"""

import anthropic
import base64
import sys

# YOUR API KEY HERE (get from console.anthropic.com)
API_KEY = "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"




def analyze_electrical_drawing(image_path):
    """
    Upload electrical drawing image and get AI analysis
    """
    
    # Read image and convert to base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Determine image type
    if image_path.lower().endswith('.png'):
        media_type = 'image/png'
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        media_type = 'image/jpeg'
    else:
        media_type = 'image/png'
    
    # Initialize Claude
    client = anthropic.Anthropic(api_key=API_KEY)
    
    # Prompt for electrical drawing analysis
    prompt = """
You are analyzing an electrical construction drawing (single line diagram, panel schedule, or site plan).

Your task:
1. Identify all electrical panels/panelboards
2. Extract panel ratings (voltage, amperage, phases)
3. Count total circuits across all panels
4. Identify wire and conduit sizes
5. Note any equipment (transformers, generators, etc.)
6. Flag any potential NEC code issues

Provide results in this format:

PANELS:
- Panel ID: [name]
  Voltage: [V]
  Amperage: [A]
  Phases: [1 or 3]
  Breaker spaces: [count]

CIRCUITS:
- Total circuits: [count]
- Wire sizes used: [AWG sizes]
- Conduit sizes used: [sizes]

EQUIPMENT:
- [List any major equipment]

MATERIAL TAKEOFF:
- [Estimated quantities of key materials]

CODE NOTES:
- [Any NEC concerns or violations]

If you cannot read certain details clearly, state that explicitly.
"""

    # Call Claude Vision API
    print("Analyzing drawing with Claude Vision...")
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )
    
    # Extract response
    result = message.content[0].text
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_claude_vision.py <path-to-drawing-image>")
        print("Example: python test_claude_vision.py single_line.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"TESTING CLAUDE VISION ON: {image_path}")
    print(f"{'='*60}\n")
    
    try:
        result = analyze_electrical_drawing(image_path)
        
        print("ANALYSIS RESULTS:")
        print("="*60)
        print(result)
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you:")
        print("1. Added your API key to the script")
        print("2. Have anthropic package installed: pip install anthropic")
        print("3. Have credit in your Anthropic account")
