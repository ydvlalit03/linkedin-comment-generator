import re

files_to_fix = [
    'app/services/profile_analyzer_gemini.py',
    'app/services/comment_generator_gemini.py'
]

for filepath in files_to_fix:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add response_mime_type to all generation_config blocks that don't have it
    pattern = r'(generation_config=genai\.types\.GenerationConfig\([^)]+)(max_output_tokens=\d+,?)([^)]*)\)'
    
    def add_json_mode(match):
        pre = match.group(1)
        tokens = match.group(2)
        post = match.group(3)
        
        if 'response_mime_type' not in post:
            # Add JSON mode if not present
            return f'{pre}{tokens}\n                    response_mime_type="application/json",{post})'
        return match.group(0)
    
    new_content = re.sub(pattern, add_json_mode, content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Updated {filepath}")

print("Done!")