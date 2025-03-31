import requests
import os
import json
import base64
import time
from typing import Optional

# --- Configuration ---
# !! IMPORTANT: Set your Fal.ai API Key !!
# Best practice: Use an environment variable `FAL_API_KEY`
# Example: export FAL_API_KEY='your_fal_key_here'
FAL_API_KEY = os.environ.get("FAL_API_KEY") # Replace default or set env var
FAL_API_URL = "https://fal.run/fal-ai/stable-audio"
API_REQUEST_TIMEOUT_SECONDS = 120 # Timeout for the main API call (can take time)
AUDIO_DOWNLOAD_TIMEOUT_SECONDS = 60 # Timeout for downloading the generated audio URL

# --- Music Generation Function ---

def generate_and_save_music(
    prompt: str,
    duration_seconds: int,
    output_filepath: str
) -> bool:
    """
    Generates music using the Fal.ai Stable Audio API and saves it locally.

    Args:
        prompt: Text description of the music to generate.
        duration_seconds: Desired duration of the music in seconds.
        output_filepath: Full path (including directory and filename with extension,
                         e.g., 'output/music/intro_bgm.wav') to save the audio.

    Returns:
        True if music generation and saving were successful, False otherwise.
    """

    if not FAL_API_KEY or FAL_API_KEY == "YOUR_FAL_API_KEY_HERE":
        print("Error: Fal.ai API Key is missing. Please set the FAL_API_KEY.")
        return False
    print(f"Requesting music generation for prompt: '{prompt[:60]}...' (Duration: {duration_seconds}s)")

    # 1. Prepare request payload and headers
    payload = {
        "prompt": prompt,
        "seconds_total": duration_seconds,
        "steps": 50 # As used in the Go example, adjust if needed
    }
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    audio_content = None # Initialize variable to hold audio bytes

    try:
        # 2. Make the POST request to Fal.ai API
        print(f"Calling Fal.ai API at {FAL_API_URL}...")
        response = requests.post(
            FAL_API_URL,
            headers=headers,
            json=payload,
            timeout=API_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status() # Check for HTTP errors (4xx, 5xx)

        # 3. Process the API response
        api_response_data = response.json()
        # print(f"API Response Data: {json.dumps(api_response_data, indent=2)}") # Debugging

        audio_url = api_response_data.get("audio_file", {}).get("url")

        if not audio_url:
            print(f"Error: API response did not contain an audio file URL.")
            print(f"Full response: {api_response_data}")
            return False

        print(f"Received audio URL: {audio_url[:100]}...") # Print truncated URL

        # 4. Handle Audio URL (Data URI or HTTP URL)
        if audio_url.startswith("data:"):
            print("Decoding base64 data URI...")
            try:
                # Format is typically "data:[<mediatype>][;base64],<data>"
                header, encoded_data = audio_url.split(",", 1)
                audio_content = base64.b64decode(encoded_data)
                print(f"Successfully decoded base64 data ({len(audio_content)} bytes).")
            except (ValueError, base64.binascii.Error) as decode_err:
                print(f"Error: Failed to parse or decode base64 data URI: {decode_err}")
                return False
        else:
            print(f"Downloading audio from URL: {audio_url}...")
            try:
                download_response = requests.get(
                    audio_url,
                    timeout=AUDIO_DOWNLOAD_TIMEOUT_SECONDS,
                    stream=True
                )
                download_response.raise_for_status() # Check download request status

                # Read content - use response.content for direct download
                audio_content = download_response.content
                print(f"Successfully downloaded audio ({len(audio_content)} bytes).")

            except requests.exceptions.Timeout:
                print(f"Error: Audio download timed out after {AUDIO_DOWNLOAD_TIMEOUT_SECONDS} seconds.")
                return False
            except requests.exceptions.HTTPError as http_err_download:
                print(f"Error: Failed to download audio. URL returned HTTP error: {http_err_download}")
                try:
                     print(f"Download error details: {download_response.text}")
                except Exception:
                     pass
                return False
            except requests.exceptions.RequestException as req_err_download:
                print(f"Error: Failed to connect to audio download URL {audio_url}. Error: {req_err_download}")
                return False

        # 5. Save the audio content to the specified file
        if audio_content:
            print(f"Saving audio to: {output_filepath}")
            try:
                # Ensure the output directory exists
                output_dir = os.path.dirname(output_filepath)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                with open(output_filepath, 'wb') as f:
                    f.write(audio_content)

                print(f"Successfully saved music audio to {output_filepath}")
                return True
            except OSError as os_err:
                print(f"Error: Failed to write audio file to {output_filepath}. Error: {os_err}")
                return False
        else:
            # This case should ideally be caught earlier, but added as a safeguard
            print("Error: No audio content was retrieved to save.")
            return False

    except requests.exceptions.Timeout:
        print(f"Error: Fal.ai API request timed out after {API_REQUEST_TIMEOUT_SECONDS} seconds.")
        return False
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: Fal.ai API returned HTTP error: {http_err}")
        try:
            print(f"API error details: {response.text}") # Show error from API if possible
        except Exception:
            pass # Ignore errors reading the error response body
        return False
    except requests.exceptions.RequestException as req_err:
        print(f"Error: Failed to connect to Fal.ai API at {FAL_API_URL}. Error: {req_err}")
        return False
    except json.JSONDecodeError as json_err:
        print(f"Error: Failed to parse JSON response from Fal.ai API. Error: {json_err}")
        try:
            print(f"Received non-JSON response: {response.text}")
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"An unexpected error occurred during music generation: {e}")
        return False


# # --- Example Usage ---
# if __name__ == "__main__":
#     print("--- Testing Music Generation ---")

#     # --- Configuration for Test ---
#     output_directory = "output_audio" # Same directory as dialogue for simplicity
#     output_filename = f"music_test_{int(time.time())}.wav" # Unique filename, assume WAV output
#     full_output_path = os.path.join(output_directory, output_filename)


#     # --- Another Test ---
#     test_prompt_2 = "Mysterious, slow ambient synth pad loop for thinking time"
#     test_duration_2 = 15
#     output_filename_2 = f"music_test_ambient_{int(time.time())}.wav"
#     full_output_path_2 = os.path.join(output_directory, output_filename_2)

#     print("\n--- Testing with another prompt ---")
#     success_2 = generate_and_save_music(
#         prompt=test_prompt_2,
#         duration_seconds=test_duration_2,
#         output_filepath=full_output_path_2
#     )

#     if success_2:
#         print(f"\nSecond test successful! Music saved to: {os.path.abspath(full_output_path_2)}")
#     else:
#         print("\nSecond test failed.")