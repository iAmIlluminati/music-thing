import os
import json
from typing import Any, Dict, Optional
from openai import OpenAI, OpenAIError # Use 'openai' package >= 1.0

# --- Make sure to set your OpenAI API key ---
# Best practice: Set as an environment variable `OPENAI_API_KEY`
# Example: export OPENAI_API_KEY='your_api_key_here'
# Or uncomment and set directly (less secure):
# os.environ["OPENAI_API_KEY"] = "your_api_key_here"

# Initialize OpenAI Client (expects OPENAI_API_KEY env var)
try:
    client = OpenAI()
except OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please ensure the OPENAI_API_KEY environment variable is set.")
    client = None # Set client to None if initialization fails

def get_audio_script_json(prompt_request: Dict[str, Any], model: str = "gpt-4o") -> Optional[Dict[str, Any]]:
    """
    Calls the OpenAI API with the generated prompts to get audio script JSON.

    Args:
        prompt_request: The dictionary returned by create_music_gen_prompt,
                        containing 'system_prompt' and 'prompt'.
        model: The OpenAI model to use (default: "gpt-4o").

    Returns:
        A dictionary parsed from the AI's JSON response, or None if an error occurs.
    """
    if not client:
        print("OpenAI client not initialized. Cannot make API call.")
        return None

    system_prompt = prompt_request.get("system_prompt")
    user_prompt = prompt_request.get("prompt")

    if not system_prompt or not user_prompt:
        print("Error: Missing system_prompt or prompt in the request.")
        return None

    try:
        print(f"\n--- Calling OpenAI API (Model: {model}) ---")
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"}, # Enforce JSON output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7, # Adjust creativity (0.0 to 2.0)
            # max_tokens=... # Optional: set a limit if needed
        )

        # Extract the JSON string content
        json_response_string = response.choices[0].message.content
        print("--- Raw JSON Response from API ---")
        print(json_response_string)

        # Parse the JSON string into a Python dictionary
        parsed_json = json.loads(json_response_string)
        print("\n--- Parsed JSON Object ---")
        # print(json.dumps(parsed_json, indent=2)) # Pretty print

        return parsed_json

    except OpenAIError as e:
        print(f"An OpenAI API error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from AI: {e}")
        print(f"Received: {json_response_string}") # Log the invalid response
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    # Assuming create_music_gen_prompt is in the same file or imported
    from create_music_gen_prompt import create_music_gen_prompt, AudioScriptInput

    sample_script = """
track_1:
- Welcome to the Silly Sounds Quiz! Get ready to giggle!
track_2:
- Question 1: What funny thing might make this sound?
- [SFX: CARTOON BOING]
track_3:
- Make your guess now! You have 5 seconds!
- [SFX: FAST Ticking Clock for 5 seconds]
track_4:
- Did you guess a bouncy spring? Or maybe a kangaroo on a pogo stick? Haha!
"""

    input_data = AudioScriptInput(
        script=sample_script,
        quiz_theme="Silly Sounds",
        mood="Goofy and Playful",
        target_age="Kids (6-10 years)"
    )

    # 1. Generate the prompt request
    prompt_req = create_music_gen_prompt(input_data)

    # Check if prompt generation was successful (it returns a dict)
    if prompt_req:
        # 2. Call the OpenAI API with the request
        audio_json_output = get_audio_script_json(prompt_req, model="gpt-4o") # Specify gpt-4o

        if audio_json_output:
            print("\n--- Final Parsed Audio Script JSON ---")
            print(json.dumps(audio_json_output, indent=2))
            # Now you can use this 'audio_json_output' dictionary
            # for further processing (e.g., feeding to an audio generation engine)
        else:
            print("\nFailed to get valid JSON response from OpenAI.")
    else:
        print("Failed to generate prompt request.")