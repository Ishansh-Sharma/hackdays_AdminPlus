import os
from gradio_client import Client, file, handle_file
from dotenv import load_dotenv
import google.generativeai as genai
import json
import textwrap

load_dotenv()
HF_TOKEN = os.getenv("HuggingFace_API")
print("API key loaded")

# fuck bitch .. api load ho gyi .. ab dekho ..
# time stamp - 11:22
# ts - 11:34 - made and upload sample form

print("q")
client = Client("merterbak/DeepSeek-OCR-Demo", hf_token=HF_TOKEN)
result_image = client.predict(
    file_path=handle_file('/Users/ishanshsharma/HackAI/MLH/Filled_Sample_form.pdf'),
    api_name="/load_image"
)
print(result_image, type(result_image))

client = Client("merterbak/DeepSeek-OCR-Demo")
result_toggle = client.predict(
    task="📋 Markdown",
    api_name="/toggle_prompt"
)
print(result_toggle)

client = Client("merterbak/DeepSeek-OCR-Demo")
result = client.predict(
    image=handle_file(f'{result_image}'),
    file_path=handle_file('/Users/ishanshsharma/HackAI/MLH/Filled_Sample_form.pdf'),
    mode="Gundam",
    task="📋 Markdown",
    custom_prompt="Hello!!",
    api_name="/run"
)
print(result)

# time stamp - 1:41

print("\n--- Starting Gemini Validation ---")

# 1. Setup Gemini
gemini_api_key = os.getenv("Gemini_api_key")
if not gemini_api_key:
    raise ValueError("Gemini_api_key not found in .env file.")

genai.configure(api_key=gemini_api_key)
# Using gemini-pro for this complex task
model = genai.GenerativeModel('gemini-pro') 
print("Gemini client configured.")

# 2. Extract the text from your 'result' variable
# Your 'result' is a tuple. The raw text is the second item (index 1).
try:
    raw_ocr_text = result[1]
    print("Extracted text from OCR result.")
except (TypeError, IndexError):
    print(f"Error: Could not extract text from 'result' variable. Result was: {result}")
    exit()

# 3. Define the validation prompt
validation_prompt = textwrap.dedent(f"""
You are an expert at parsing and validating structured documents from raw OCR text.
The user has submitted a "Mantoux Tuberculin Skin Test Record Form".

I need you to do two things:
1.  Extract the "Patient Information Name".
2.  Validate that the form is "correct". A "correct" form *must* have text filled in for these 4 fields:
    - Patient Information Name
    - Address
    - Administrator Name
    - Results Induration

Here is the raw OCR text:
---
{raw_ocr_text}
---

Analyze the text. Check if all 4 required fields are present and *filled in*.

Respond with ONLY a single JSON object. Do not add any other text.
The JSON format must be:
{{
  "student_name": "The extracted name or 'Not Found'",
  "is_correct": true_or_false,
  "missing_fields": ["list of missing fields", "or an empty list"]
}}
""")

# 4. Call Gemini and print the final JSON
try:
    print("Sending OCR text to Gemini for validation...")
    response = model.generate_content(validation_prompt)
    
    # Clean up the response to get just the JSON
    json_response_str = response.text.strip().replace("```json", "").replace("```", "")
    
    print("Gemini validation successful.")
    
    # Parse the JSON string into a Python dictionary
    final_json = json.loads(json_response_str)
    
    print("\n--- FINAL VALIDATION JSON (from terminal) ---")
    # Pretty-print the final JSON to the terminal
    print(json.dumps(final_json, indent=2))
    
    # --- !! NEW CODE TO SAVE THE FILE !! ---
    output_filename = "validation_result.json"
    with open(output_filename, "w") as f:
        # Write the 'final_json' dictionary to the file
        json.dump(final_json, f, indent=2)
    
    print(f"\n--- SUCCESS! VALIDATION SAVED TO: {output_filename} ---")

except Exception as e:
    print(f"Gemini validation failed: {e}")
    if 'response' in locals():
        print(f"Gemini's raw response (if any): {response.text}")