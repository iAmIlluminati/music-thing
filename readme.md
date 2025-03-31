# Audio Quiz Generator

A comprehensive system for automatically generating educational audio quizzes with dialogue, background music, and sound effects.

## Overview

This project creates engaging audio quizzes by:

1. Converting a simple text script into a structured audio production plan using AI
2. Generating spoken dialogue using a text-to-speech (TTS) service
3. Creating appropriate background music and sound effects using Fal.ai's Stable Audio API
4. Combining all audio components into a final production-ready audio file

Perfect for educational content creators, teachers, or anyone looking to create interactive audio quizzes without complex audio editing skills.

## Features

- Convert simple text scripts into complete audio productions
- Generate natural-sounding dialogue with configurable speaker voices
- Create custom background music and sound effects based on text descriptions
- Automatically mix dialogue and music with appropriate volume levels
- Export final audio in MP3 format, ready for distribution

## Requirements

- Python 3.7+
- OpenAI API key (for GPT-4o)
- Fal.ai API key (for Stable Audio)
- Access to the TTS API service (configured in `dialogue_gen.py`)
- FFmpeg (for audio processing with pydub)
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/audio-quiz-generator.git
   cd audio-quiz-generator
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install openai requests pydub
   ```

4. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Configuration

Set up your API keys as environment variables:

```bash
# For OpenAI API
export OPENAI_API_KEY="your-openai-api-key"

# For Fal.ai Stable Audio
export FAL_API_KEY="your-fal-ai-api-key"
```

On Windows, use:
```bash
set OPENAI_API_KEY=your-openai-api-key
set FAL_API_KEY=your-fal-ai-api-key
```

## Usage

### Basic Usage

Run the main script to generate an audio quiz:

```bash
python main.py
```

This will:
1. Use the sample script defined in `main.py`
2. Generate an appropriate audio structure using GPT-4o
3. Create dialogue and music components
4. Combine everything into a final audio file in the `final_audio_output` directory

### Custom Quiz Scripts

To create your own audio quiz, modify the `sample_script` in `main.py`:

```python
sample_script = """
track_1:
- Welcome to your custom quiz!
track_2:
- Question 1: Your question here
- [SFX: DESCRIPTION OF SOUND EFFECT]
track_3:
- Thinking time... 5 seconds!
track_4:
- The correct answer is...
track_5:
- Well done if you got it right!
"""

input_data = prompt.AudioScriptInput(
    script=sample_script,
    quiz_theme="Your Quiz Theme",
    mood="Desired Mood",
    target_age="Target Age Group"
)
```


## Project Structure

- `main.py` - Main script that orchestrates the entire process
- `prompt.py` - Creates structured prompts for the OpenAI API
- `call_openai_api.py` - Handles communication with OpenAI API
- `dialogue_gen.py` - Generates speech using the TTS service
- `music_gen.py` - Creates music using Fal.ai Stable Audio API
- `.gitignore` - Specifies files to ignore in version control

## Audio Processing Details

The system:
1. Breaks down the script into tracks and events
2. For dialogue events, generates both speech and background music
3. For standalone sound effects, generates appropriate audio
4. Reduces music volume (by 20dB) when overlaid with dialogue
5. Combines all audio segments in sequence
6. Exports as a single MP3 file

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure OPENAI_API_KEY and FAL_API_KEY are set correctly

2. **FFmpeg Not Found**
   - Verify FFmpeg is installed and in your system PATH
   - Alternatively, specify the path explicitly in the code:
     ```python
     from pydub import AudioSegment
     AudioSegment.converter = "/path/to/ffmpeg"
     AudioSegment.ffprobe = "/path/to/ffprobe"
     ```

3. **TTS API Connection Failed**
   - Check if the TTS service is running and accessible
   - Verify the URL in `dialogue_gen.py` is correct

4. **Audio File Export Errors**
   - Ensure you have write permissions for the output directory
   - Check disk space availability

## License

This project is released under the MIT License. See the LICENSE file for details.

## Future Improvements

- Add a command-line interface for easier script input
- Support for multiple TTS voices in the same quiz
- Web interface for script editing and preview
- More customization options for audio mixing
- Support for additional audio formats

## Credits

This project uses:
- [OpenAI API](https://openai.com/) for script generation
- [Fal.ai Stable Audio](https://fal.ai/) for music generation
- [Pydub](https://github.com/jiaaro/pydub) for audio processing