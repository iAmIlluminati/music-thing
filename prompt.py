import dataclasses
import json
from typing import Optional, Dict, Any

@dataclasses.dataclass
class AudioScriptInput:
    """Represents input for creating music and SFX for dialogue scripts"""
    script: str                      # The dialogue script with track divisions
    quiz_theme: Optional[str] = None # Optional theme (e.g., "Solar System")
    mood: Optional[str] = None       # Optional mood (e.g., "Playful")
    target_age: Optional[str] = None # Optional target age (e.g., "Children")

def create_music_gen_prompt(input_data: AudioScriptInput) -> Dict[str, Any]:
    """
    Generates a structured prompt request for creating music and SFX
    for dialogue scripts, suitable for an AI model.

    Args:
        input_data: An AudioScriptInput object containing the script and
                    optional theme, mood, and target age.

    Returns:
        A dictionary containing the 'system_prompt', 'prompt' (user message),
        and 'json_out_example' (description of expected JSON format).
    """
    # Set default values if not specified
    quiz_theme = input_data.quiz_theme or "Educational Quiz"
    mood = input_data.mood or "Playful and Engaging"
    target_age = input_data.target_age or "Children"

    # Build the complete user prompt
    # Use triple quotes for multi-line f-string
    complete_prompt = f"""
# Music and Sound Effects Generation for Educational Audio Quiz

## Script:
{input_data.script}

## Quiz Theme: {quiz_theme}
## Overall Mood: {mood}
## Target Audience: {target_age}

Create appropriate music and sound effects descriptions for each track in this audio quiz script. The music should enhance the educational experience while keeping the listeners engaged. Generate the response following the JSON structure provided in the system instructions.
"""

    # Define the expected JSON output format description (for context, primarily used in system prompt)
    # Using raw triple quotes r"""...""" helps avoid issues with backslashes if any were present
    json_out_example = r"""{
  "overall_bgm": "DESCRIPTION OF CONSISTENT BACKGROUND MUSIC THAT PLAYS THROUGHOUT THE ENTIRE QUIZ. JUST EXPLAIN THE MUSIC, THE BEAT, INSTRUMENTS AND MOOD",
  "script": [
     [
        {
          "dialogue": "DIALOGUE TEXT FOR TTS",
          "music": "DESCRIPTION OF BACKGROUND MUSIC/SFX THAT PLAYS DURING THIS DIALOGUE"
        },
        {
          "music": "DESCRIPTION OF STANDALONE MUSIC OR SFX",
          "duration": INTEGER_DURATION_IN_SECONDS
        }
    ],

    [
        {
          "music": "DESCRIPTION OF STANDALONE MUSIC OR SFX",
          "duration": INTEGER_DURATION_IN_SECONDS
        }
    ]
  ]
}"""

    # Define the system prompt
    # Using raw triple quotes r"""..."""
    system_prompt = r"""You are an expert audio designer specializing in creating music and sound effects for educational audio content.

Your task is to create appropriate music and sound effect descriptions for an audio quiz script based on the user's input. Follow these guidelines precisely:

1.  **Overall Background Music (BGM):**
    *   Create a description for consistent background music (BGM) that fits the provided theme, mood, and target audience.
    *   The BGM should be subtle enough not to overpower the dialogue but present enough to maintain engagement.
    *   Specify style, instrumentation, tempo (e.g., upbeat but gentle), and overall feeling.

2.  **Track-Specific Audio (`script` array):**
    *   The `script` key in the JSON output must contain a list of lists. Each inner list represents a "track" from the input script (corresponding to track_1, track_2, etc.).
    *   Each track (inner list) contains one or more dictionary objects representing audio events within that track.
    *   **Dialogue Event:** If an event includes dialogue, the dictionary MUST contain:
        *   `"dialogue"`: The exact dialogue text provided in the input script for that segment.
        *   `"music"`: A description of the background music or sound effect that should play *concurrently* with this specific dialogue line. This might be a continuation of the overall BGM, a variation, or a specific SFX cue.
    *   **Standalone Music/SFX Event:** If an event is purely musical or a sound effect without concurrent dialogue, the dictionary MUST contain:
        *   `"music"`: A description of the standalone music piece (e.g., intro jingle, thinking music, answer reveal fanfare) or sound effect (e.g., ticking clock, correct answer chime, transition swoosh).
        *   `"duration"`: An integer representing the duration of this standalone audio event in seconds. This key MUST NOT be present if the `"dialogue"` key is present.
    *   Ensure the audio described for each track element logically enhances the content (e.g., intro music, question background, thinking pause, result sounds).

3.  **Music/SFX Description Quality:**
    *   Descriptions must be specific and actionable for an audio generation system or sound designer. Mention style (e.g., light orchestral, quirky electronic, ambient), instruments (e.g., ukulele, synth pads, xylophone), tempo (e.g., allegro, lento), mood (e.g., mysterious, celebratory, focused), and specific SFX sounds (e.g., gentle 'ding', cartoon 'boing', futuristic 'whoosh').
    *   Keep the target audience and overall mood in mind for all descriptions.

4.  **Output Format:**
    *   You MUST reply ONLY with a valid JSON object.
    *   Do not include any explanatory text before or after the JSON object.
    *   The JSON object must strictly adhere to the structure exemplified below:
        ```json
        {
          "overall_bgm": "DESCRIPTION",
          "script": [
             [ {"dialogue": "TEXT", "music": "DESC"}, {"music": "DESC", "duration": N (mandtory)} ],
             [ {"music": "DESC", "duration": N} ]
          ]
        }

        THE DURATION IS MANDATORY IF YOU HAVE JUST THE MUSIC FIELD AS ELEMENT
        
        ```

REPLY ONLY AS A VALID JSON OBJECT.
"""

    return {
        "prompt": complete_prompt,
        "json_out_example": json_out_example, # Kept for reference, but primary guide is in system prompt
        "system_prompt": system_prompt,
    }

# --- Example Usage ---
if __name__ == "__main__":
    sample_script = """
track_1:
- Welcome to the Animal Sounds Quiz!
track_2:
- Question 1: What animal makes this sound?
- [SFX: COW MOOING]
track_3:
- Time's up!
track_4:
- The answer was: Cow!
"""

    input_data = AudioScriptInput(
        script=sample_script,
        quiz_theme="Animal Sounds",
        mood="Fun and Educational",
        target_age="Preschoolers (3-5 years)"
    )

    prompt_request = create_music_gen_prompt(input_data)

    print("--- System Prompt ---")
    print(prompt_request["system_prompt"])
    print("\n--- User Prompt (Message) ---")
    print(prompt_request["prompt"])
    print("\n--- Example JSON Structure (for reference) ---")
    print(prompt_request["json_out_example"])