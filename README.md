# YouTube MP3 Transcriber

A Python tool to download YouTube videos as MP3 files and transcribe them using OpenAI's Whisper model.

## Features

- Download YouTube videos as MP3 files
- Transcribe audio files using OpenAI's Whisper model
- Save transcriptions as text files
- Avoid IP bans by using proper rate limiting
- Batch processing with configurable delays

## Requirements

- Python 3.6+
- FFmpeg (for audio processing)
- OpenAI API key (for transcription)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-mp3-transcriber.git
   cd youtube-mp3-transcriber
   ```

2. Create a virtual environment and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Make sure FFmpeg is installed on your system:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

### Single Video Download and Transcription

```bash
python youtube_mp3_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" --api-key "your_openai_api_key"
```

#### Command Line Arguments

- `url`: YouTube video URL (required)
- `--output-dir`: Output directory for downloaded files (default: "downloads")
- `--api-key`: OpenAI API key (can also be set as OPENAI_API_KEY environment variable)
- `--skip-transcription`: Skip the transcription step and only download the MP3

### Batch Processing with Rate Limiting

For downloading multiple videos while avoiding IP bans, use the batch downloader:

```bash
python youtube_batch_downloader.py --input-file sample_urls.txt --api-key "your_openai_api_key"
```

#### Command Line Arguments

- `--input-file`: File containing YouTube URLs, one per line (required)
- `--output-dir`: Output directory for downloaded files (default: "downloads")
- `--api-key`: OpenAI API key (can also be set as OPENAI_API_KEY environment variable)
- `--min-delay`: Minimum delay between downloads in seconds (default: 30)
- `--max-delay`: Maximum delay between downloads in seconds (default: 120)
- `--skip-transcription`: Skip the transcription step and only download the MP3s

### Environment Variables

You can set your OpenAI API key as an environment variable instead of passing it as a command-line argument:

```bash
export OPENAI_API_KEY="your_openai_api_key"
python youtube_mp3_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Cost Considerations

This project uses OpenAI's Whisper API for transcription, which is billed based on the duration of the audio file. The Whisper-1 model is used, which is the most cost-effective option for transcription.

Current pricing (as of 2024):
- Whisper-1: $0.006 per minute

For a 10-minute video, the cost would be approximately $0.06.

## License

MIT 