# Seedance Video Generator

A GUI application for generating AI-powered videos using the Seedance API from ByteDance.

## Prerequisites

- Python 3.7 or higher
- macOS, Windows, or Linux
- Ark API key from ByteDance

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd seedance_vidgen
```

2. Create and activate a virtual environment:

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Set up your API key:

## Usage

1. Run the application:

```bash
python main.py
```

2. The GUI window will open with the following sections:

### Video Parameters

- **Aspect Ratio**: Choose between 16:9 (landscape) or 9:16 (portrait)
- **Resolution**: Select 720p or 1080p
- **Duration**: Pick 5 or 10 seconds

### Creating Videos

1. **Enter a prompt**: Type your video description in the text area

   - Example: "广角航拍镜头展现旧金山黄昏时分——雾气缓缓飘来，城市灯光闪烁。"

2. **Optimize your prompt** (optional):

   - Click "Fix Prompt" to use AI to enhance your prompt
   - The AI will add professional video generation terminology

3. **Generate video**:
   - Click "Generate Video" to start the process
   - Watch the progress bar and status updates
   - The video will be automatically downloaded when complete

### Output

- Videos are saved in the project directory as `seedance_video_[timestamp].mp4`
- Generation typically takes 30-60 seconds
- Check the Output Log for detailed status information

## Troubleshooting

### tkinter not found error

If you get a tkinter error on macOS:

```bash
brew install python-tk@3.13
```

### API Key issues

- Make sure your `.env` file contains a valid API key
- Ensure the API key has permissions for both video generation and chat completions
