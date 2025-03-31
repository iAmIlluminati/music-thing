import requests
import os
import time
from typing import Optional

# --- Configuration ---
# You can keep the URL here or load it from configuration/environment variables
TTS_API_URL = "http://144.24.138.210:5000/"
REQUEST_TIMEOUT_SECONDS = 30 # Timeout for the HTTP request

# --- Dialogue Generation Function ---

def generate_and_save_dialogue(
    text: str,
    speaker_id: int,
    output_filepath: str
) -> bool:
    """
    Generates dialogue audio using a TTS service and saves it to a local file.

    Args:
        text: The text content to convert to speech.
        speaker_id: The integer ID of the desired speaker voice.
        output_filepath: The full path (including directory and filename with extension,
                         e.g., 'output/audio/dialogue_1.wav') where the audio
                         will be saved.

    Returns:
        True if the audio was successfully generated and saved, False otherwise.
    """
    print(f"Requesting TTS for speaker {speaker_id}: '{text[:50]}...'") # Log truncated text

    # Prepare query parameters
    params = {
        "text": text,
        "speaker_id": speaker_id
    }

    try:
        # Make the GET request to the TTS service
        response = requests.get(
            TTS_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True # Use stream=True for potentially large audio files
        )

        # Check if the request was successful (status code 2xx)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir: # Only create if output_dir is not empty (i.e., not saving in current dir)
            os.makedirs(output_dir, exist_ok=True) # exist_ok=True prevents error if dir exists

        # Save the audio content to the specified file
        print(f"Saving audio to: {output_filepath}")
        with open(output_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): # Read in chunks
                f.write(chunk)

        print(f"Successfully saved dialogue audio to {output_filepath}")
        return True

    except requests.exceptions.Timeout:
        print(f"Error: TTS request timed out after {REQUEST_TIMEOUT_SECONDS} seconds.")
        return False
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: TTS service returned HTTP error: {http_err}")
        # You might want to read response.text here for more details if available
        try:
             print(f"Error details: {response.text}")
        except Exception:
             pass # Ignore errors reading the error response body
        return False
    except requests.exceptions.RequestException as req_err:
        print(f"Error: Failed to connect to TTS service at {TTS_API_URL}. Error: {req_err}")
        return False
    except OSError as os_err:
        print(f"Error: Failed to write audio file to {output_filepath}. Error: {os_err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Testing Dialogue Generation ---")

    # --- Configuration for Test ---
    test_text = "Hello! This is a test of the text-to-speech system."
    test_speaker_id = 33 # Adjust speaker ID if needed
    # Define where to save the output - creates an 'output_audio' subdir if needed
    output_directory = "output_audio"
    output_filename = f"dialogue_test_{int(time.time())}.wav" # Unique filename
    full_output_path = os.path.join(output_directory, output_filename)

    # --- Run the Function ---
    success = generate_and_save_dialogue(
        text=test_text,
        speaker_id=test_speaker_id,
        output_filepath=full_output_path
    )

    # --- Check Result ---
    if success:
        print(f"\nTest successful! Audio saved to: {os.path.abspath(full_output_path)}")
        # You can add code here to play the audio if you have a library like `sounddevice` or `playsound`
        # e.g., import playsound; playsound.playsound(full_output_path)
    else:
        print("\nTest failed. Check error messages above.")

    # print("\n--- Testing with a different speaker ---")
    # for i in range(0,100):
    #     test_text_2 = "This is another test with a different voice."
    #     test_speaker_id_2 = i # Try a different speaker ID
    #     output_filename_2 = f"dialogue_test_speaker{test_speaker_id_2}_{int(time.time())}.wav"
    #     full_output_path_2 = os.path.join(output_directory, output_filename_2)

    #     success_2 = generate_and_save_dialogue(
    #         text=test_text_2,
    #         speaker_id=test_speaker_id_2,
    #         output_filepath=full_output_path_2
    #     )

    # if success_2:
    #     print(f"\nSecond test successful! Audio saved to: {os.path.abspath(full_output_path_2)}")
    # else:
    #     print("\nSecond test failed.")