import json
import os
import time
import shutil # For removing temporary directory
import math
from typing import Optional
from call_openai_api import get_audio_script_json
import prompt # Assuming prompt.py contains AudioScriptInput and create_music_gen_prompt
from dialogue_gen import generate_and_save_dialogue
from music_gen import generate_and_save_music

# --- Pydub Setup ---
# Make sure ffmpeg or libav is installed and accessible in your PATH
# If not in PATH, you might need to specify the path explicitly:
# from pydub.utils import get_player_name, get_prober_name
# AudioSegment.converter = "C:\\path\\to\\ffmpeg\\bin\\ffmpeg.exe" # Example for Windows
# AudioSegment.ffprobe   = "C:\\path\\to\\ffmpeg\\bin\\ffprobe.exe"
try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub library not found. Please install it: pip install pydub")
    print("You also need ffmpeg or libav installed on your system.")
    AudioSegment = None # Set to None to prevent runtime errors later if import fails

# --- Configuration ---
OUTPUT_DIR = "final_audio_output"
TEMP_AUDIO_DIR = os.path.join(OUTPUT_DIR, "temp_audio")
DIALOGUE_SPEAKER_ID = 33 # As requested
MUSIC_OVERLAY_VOLUME_REDUCTION_DB = 20 # Reduce music volume by 20 dB for overlay (approx 10% amplitude)
BGM_OVERLAY_VOLUME_REDUCTION_DB = 26 # Reduce BGM volume by 26 dB for overlay (approx 5% amplitude)
BGM_DURATION_SECONDS = 30 # Generate a 30-second BGM track

def get_audio_duration_ms(filepath: str) -> Optional[int]:
    """Gets the duration of an audio file in milliseconds using pydub."""
    if not AudioSegment: return None
    try:
        audio = AudioSegment.from_file(filepath)
        return len(audio) # pydub duration is in milliseconds
    except Exception as e:
        print(f"Error getting duration for {filepath}: {e}")
        return None

def main():
    """
    Main function to define input, generate prompt, call API,
    generate audio components, and combine them.
    """
    if not AudioSegment:
        print("Cannot proceed without pydub library and its dependencies (ffmpeg/libav).")
        return

    print("Starting Audio Quiz Script Generation and Production...")

    # --- 1. Define Input & Get AI Script ---
    sample_script = """
Track 1

Excited voice of a quiz master 

Hello and welcome to the “Solar System” Quiz! 
My name is Milo and I have a very fun quiz for you today! I will ask you a question and give you four choices. You will have ten seconds to answer each question. 
If you’re ready with the answer, just say ‘Ready’

Track 2

Let’s go!

Track 3

Tense music

Music fades

Track 4

Which sea creature has eight arms?

Track 5

Light background music - sea sounds

Squid
Jellyfish
Lion Fish
Octopus

Track 6

10 sec Countdown timer sfx

Track 7

The correct answer is option d Octopus. 

Track 8

Congratulations.
Your answer is right. You get 5 points.
Applause sound 

Track 9

If you got it wrong, no problem, you’ll get the next one. Here we go!

"""

    input_data = prompt.AudioScriptInput(
        script=sample_script,
        quiz_theme="Solar System Exploration",
        mood="Exciting and Educational",
        target_age="Children (8-12 years)"
    )
    print(f"Input Theme: {input_data.quiz_theme}, Mood: {input_data.mood}, Target Age: {input_data.target_age}")

    print("\nGenerating prompt for AI...")
    prompt_req = prompt.create_music_gen_prompt(input_data)

    if not prompt_req:
        print("Error: Failed to generate prompt request.")
        return

    print("\nCalling OpenAI API for audio script structure...")
    audio_json_output = get_audio_script_json(prompt_req, model="gpt-4o")

    if not audio_json_output:
        print("\n--- Failed to get valid JSON response from OpenAI ---")
        return

    print("\n--- Successfully Received and Parsed Audio Script JSON ---")
    # print(json.dumps(audio_json_output, indent=2)) # Optionally print the received JSON

    # --- 2. Setup Output Directories ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Clean up temp directory if it exists from a previous run
    if os.path.exists(TEMP_AUDIO_DIR):
        shutil.rmtree(TEMP_AUDIO_DIR)
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    print(f"Created temporary directory: {TEMP_AUDIO_DIR}")

    # --- 3. Process JSON and Generate Audio Components ---
    final_audio = AudioSegment.empty() # Initialize empty audio segment for combining
    script_data = audio_json_output.get("script")

    if not script_data or not isinstance(script_data, list):
        print("Error: 'script' key missing or not a list in the JSON response.")
        return

    processing_successful = True # Flag to track if all steps succeed

    try: # Use try...finally to ensure temp dir cleanup
        for i, track_data in enumerate(script_data):
            print(f"\n--- Processing Track {i+1} ---")
            if not isinstance(track_data, list):
                print(f"Warning: Track {i+1} data is not a list, skipping.")
                continue

            track_audio = AudioSegment.empty()

            for j, event in enumerate(track_data):
                event_audio = None
                event_label = f"track_{i+1}_event_{j+1}"
                print(f"  Processing Event {j+1}: {list(event.keys())}") # Show keys in the event dict

                # --- Case 1: Dialogue with Background Music ---
                if "dialogue" in event and "music" in event:
                    dialogue_text = event["dialogue"]
                    music_prompt = event["music"]
                    dialogue_filename = f"{event_label}_dialogue.wav"
                    music_filename = f"{event_label}_music.wav"
                    dialogue_filepath = os.path.join(TEMP_AUDIO_DIR, dialogue_filename)
                    music_filepath = os.path.join(TEMP_AUDIO_DIR, music_filename)

                    print(f"    Generating dialogue: '{dialogue_text[:50]}...'")
                    if not generate_and_save_dialogue(dialogue_text, DIALOGUE_SPEAKER_ID, dialogue_filepath):
                        print(f"    ERROR: Failed to generate dialogue for event {j+1}. Skipping event.")
                        processing_successful = False
                        continue # Skip this event

                    # Get dialogue duration to generate music of the same length
                    dialogue_duration_ms = get_audio_duration_ms(dialogue_filepath)
                    if dialogue_duration_ms is None:
                         print(f"    ERROR: Could not get duration for {dialogue_filepath}. Skipping event.")
                         processing_successful = False
                         continue

                    # Music generation often takes integer seconds, round up
                    music_duration_sec = math.ceil(dialogue_duration_ms / 1000)
                    print(f"    Dialogue duration: {dialogue_duration_ms / 1000:.2f}s. Generating music for {music_duration_sec}s.")
                    print(f"    Generating music: '{music_prompt[:50]}...'")
                    if not generate_and_save_music(music_prompt, music_duration_sec, music_filepath):
                        print(f"    ERROR: Failed to generate music for event {j+1}. Using dialogue only.")
                        # Proceed with just dialogue if music fails
                        try:
                            event_audio = AudioSegment.from_wav(dialogue_filepath)
                        except Exception as e:
                            print(f"      ERROR loading dialogue audio {dialogue_filepath}: {e}")
                            processing_successful = False
                        continue # Go to next event

                    # Load both and overlay
                    try:
                        dialogue_segment = AudioSegment.from_wav(dialogue_filepath)
                        music_segment = AudioSegment.from_wav(music_filepath)

                        # Ensure music is at least as long as dialogue (it might be slightly longer due to rounding up)
                        # Trim music if needed, though overlay handles mismatched lengths
                        # music_segment = music_segment[:dialogue_duration_ms]

                        print(f"    Overlaying music (reduced by {MUSIC_OVERLAY_VOLUME_REDUCTION_DB} dB)")
                        quieter_music = music_segment - MUSIC_OVERLAY_VOLUME_REDUCTION_DB
                        event_audio = dialogue_segment.overlay(quieter_music)

                    except Exception as e:
                         print(f"    ERROR loading or overlaying audio for event {j+1}: {e}")
                         processing_successful = False
                         # Attempt to use just dialogue if overlay fails
                         try:
                            event_audio = AudioSegment.from_wav(dialogue_filepath)
                            print("      Using dialogue audio only due to overlay error.")
                         except Exception as load_err:
                             print(f"      ERROR loading dialogue audio after overlay failure: {load_err}")


                # --- Case 2: Standalone Music/SFX ---
                elif "music" in event and "duration" in event and "dialogue" not in event:
                    music_prompt = event["music"]
                    duration_sec = event["duration"]
                    music_filename = f"{event_label}_standalone_music.wav"
                    music_filepath = os.path.join(TEMP_AUDIO_DIR, music_filename)

                    if not isinstance(duration_sec, int) or duration_sec <= 0:
                        print(f"    Warning: Invalid duration ({duration_sec}) for standalone music in event {j+1}. Skipping.")
                        continue

                    print(f"    Generating standalone music/sfx for {duration_sec}s: '{music_prompt[:50]}...'")
                    if not generate_and_save_music(music_prompt, duration_sec, music_filepath):
                        print(f"    ERROR: Failed to generate standalone music for event {j+1}. Skipping event.")
                        processing_successful = False
                        continue

                    # Load the generated music
                    try:
                        event_audio = AudioSegment.from_wav(music_filepath)
                    except Exception as e:
                         print(f"    ERROR loading standalone music audio {music_filepath}: {e}")
                         processing_successful = False

                # --- Invalid Event Structure ---
                else:
                    print(f"    Warning: Skipping event {j+1} due to unrecognized structure: {event}")
                    continue

                # Append the processed audio for this event to the current track's audio
                if event_audio:
                    track_audio += event_audio
                    print(f"    Appended {len(event_audio)/1000:.2f}s to track {i+1}")


            # Append the complete track audio to the final audio
            if len(track_audio) > 0:
                final_audio += track_audio
                print(f"  Completed Track {i+1}, Total duration now: {len(final_audio)/1000:.2f}s")
            else:
                 print(f"  Warning: Track {i+1} resulted in empty audio.")

        # --- 4. Export First Combined Audio (without overall BGM) ---
        if len(final_audio) > 0 and processing_successful:
            timestamp = int(time.time())
            final_filename = f"audio_quiz_output_{timestamp}.mp3" # Export as MP3 for smaller size
            final_filepath = os.path.join(OUTPUT_DIR, final_filename)
            print(f"\n--- Exporting First Combined Audio (without overall BGM) ---")
            print(f"Saving to: {final_filepath}")
            try:
                final_audio.export(final_filepath, format="mp3")
                print(f"Successfully exported first audio file!")
            except Exception as e:
                print(f"ERROR: Failed to export first audio: {e}")
                processing_successful = False
        
        # --- 5. Generate and apply overall BGM track ---
        if len(final_audio) > 0 and processing_successful:
            # Extract overall BGM description from JSON
            overall_bgm_description = audio_json_output.get("overall_bgm", "")
            if overall_bgm_description:
                print(f"\n--- Generating Overall BGM Track (30s) ---")
                print(f"BGM Description: '{overall_bgm_description[:100]}...'")
                
                # Generate the overall BGM
                bgm_filename = f"overall_bgm_{timestamp}.wav"
                bgm_filepath = os.path.join(TEMP_AUDIO_DIR, bgm_filename)
                
                if generate_and_save_music(overall_bgm_description, BGM_DURATION_SECONDS, bgm_filepath):
                    try:
                        # Load the BGM
                        bgm_segment = AudioSegment.from_wav(bgm_filepath)
                        
                        # Calculate how many times to loop the BGM
                        final_duration_ms = len(final_audio)
                        loops_needed = math.ceil(final_duration_ms / len(bgm_segment))
                        
                        print(f"Main track duration: {final_duration_ms/1000:.2f}s")
                        print(f"BGM duration: {len(bgm_segment)/1000:.2f}s")
                        print(f"Looping BGM {loops_needed} times to cover main track")
                        
                        # Create extended BGM by looping
                        extended_bgm = bgm_segment * loops_needed
                        
                        # Trim to match main track duration exactly
                        extended_bgm = extended_bgm[:final_duration_ms]
                        
                        # Reduce volume for background
                        quieter_bgm = extended_bgm - BGM_OVERLAY_VOLUME_REDUCTION_DB
                        print(f"Applying BGM at reduced volume ({BGM_OVERLAY_VOLUME_REDUCTION_DB} dB reduction)")
                        
                        # Overlay with main track
                        final_audio_with_bgm = final_audio.overlay(quieter_bgm)
                        
                        # Export second file with BGM
                        final_with_bgm_filename = f"audio_quiz_with_bgm_{timestamp}.mp3"
                        final_with_bgm_filepath = os.path.join(OUTPUT_DIR, final_with_bgm_filename)
                        print(f"\n--- Exporting Second Combined Audio (with overall BGM) ---")
                        print(f"Saving to: {final_with_bgm_filepath}")
                        
                        final_audio_with_bgm.export(final_with_bgm_filepath, format="mp3")
                        print(f"Successfully exported second audio file with BGM!")
                        
                    except Exception as e:
                        print(f"ERROR: Failed to process or export BGM version: {e}")
                else:
                    print(f"ERROR: Failed to generate overall BGM. Skipping second audio file.")
            else:
                print(f"No overall BGM description found in the JSON response. Skipping second audio file.")
        elif not processing_successful:
             print("\n--- Final Audio Export Skipped due to errors during processing ---")
        else:
            print("\n--- No audio generated, final export skipped ---")

    except Exception as e:
        print(f"\n--- An unexpected error occurred during audio processing: {e} ---")
        processing_successful = False
    finally:
        # --- 6. Cleanup Temporary Files ---
        if os.path.exists(TEMP_AUDIO_DIR):
            print(f"\nCleaning up temporary directory: {TEMP_AUDIO_DIR}")
            try:
                shutil.rmtree(TEMP_AUDIO_DIR)
                print("Temporary directory removed.")
            except Exception as e:
                print(f"Warning: Could not remove temporary directory {TEMP_AUDIO_DIR}: {e}")

    print("\nAudio Quiz Script Generation and Production finished.")
    if not processing_successful:
         print("NOTE: There were errors during the process. Check logs above.")


if __name__ == "__main__":
    # Ensure API keys are set before running main
    keys_ok = True
    if "OPENAI_API_KEY" not in os.environ:
        print("FATAL ERROR: OPENAI_API_KEY environment variable not found.")
        keys_ok = False
    # Add check for FAL_API_KEY as it's needed by music_gen
    if "FAL_API_KEY" not in os.environ or not os.environ["FAL_API_KEY"]:
         print("FATAL ERROR: FAL_API_KEY environment variable not found or empty.")
         print("Please set the variable for Fal.ai music generation.")
         keys_ok = False

    if keys_ok:
        main()
    else:
        print("Please set the required API key environment variables and try again.")