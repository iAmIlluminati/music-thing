import json
from call_openai_api import get_audio_script_json
import prompt
import os

def main():
    """
    Main function to define input, generate prompt, call API, and print result.
    """
    print("Starting Audio Quiz Script Generation...")

    # 1. Define the Input Script and Parameters
    sample_script = """
track_1:
- Welcome explorers to the Solar System Sprint!
track_2:
- Question 1: Which planet is known as the Red Planet?
- [SFX: MYSTERIOUS WHOOSH]
track_3:
- Thinking time... 5 seconds!
- [SFX: FUTURISTIC TICKING CLOCK 5s]
track_4:
- Time is up!
track_5:
- The correct answer is... Mars!
- [SFX: CELEBRATORY CHIME]
track_6:
- Great job if you got it right! Let's move on.
"""

    input_data = prompt.AudioScriptInput(
        script=sample_script,
        quiz_theme="Solar System Exploration",
        mood="Exciting and Educational",
        target_age="Children (8-12 years)"
    )
    print(f"Input Theme: {input_data.quiz_theme}, Mood: {input_data.mood}, Target Age: {input_data.target_age}")

    # 2. Generate the Prompt Request
    print("\nGenerating prompt for AI...")
    prompt_req = prompt.create_music_gen_prompt(input_data)

    if not prompt_req:
        print("Error: Failed to generate prompt request.")
        return # Exit if prompt generation failed

    # 3. Call the OpenAI API
    audio_json_output = get_audio_script_json(prompt_req, model="gpt-4o") # Ensure gpt-4o is used

    # 4. Process and Print the Result
    if audio_json_output:
        print("\n--- Successfully Received and Parsed Audio Script JSON ---")
        print(json.dumps(audio_json_output, indent=2))
        # Here you would typically pass 'audio_json_output' to the next step
        # in your process (e.g., an audio synthesis engine).
    else:
        print("\n--- Failed to get valid JSON response from OpenAI ---")

    print("\nAudio Quiz Script Generation finished.")

if __name__ == "__main__":
    # Ensure API key is set before running main
    if "OPENAI_API_KEY" not in os.environ:
        print("FATAL ERROR: OPENAI_API_KEY environment variable not found.")
        print("Please set the variable and try again.")
        # Optionally exit here:
        # import sys
        # sys.exit(1)
    else:
        main()