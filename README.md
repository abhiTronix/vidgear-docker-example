# 🎥 VidGear Docker Streamer

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![VidGear](https://img.shields.io/badge/VidGear-Framework-green.svg?style=for-the-badge)](https://abhitronix.github.io/vidgear)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](LICENSE)

A production-ready Docker application template for the [**VidGear Python framework**](https:/'/github.com/abhiTronix/vidgear) that demonstrates video streaming, processing, and encoding with audio support. This template showcases best practices for containerizing VidGear applications with FFmpeg, GStreamer, and OpenCV.

<img src="https://abhitronix.github.io/vidgear/latest/assets/images/vidgear.png" loading="lazy" alt="Vidgear Logo" style="width: 50%;"/>
<img src="docs/assets/docker-logo-blue.png" loading="lazy" alt="Docker Logo" style="width: 20%;"/>

## ✨ Features

- 🎬 **Video Streaming**: Stream videos from YouTube, Twitch, and other platforms using yt-dlp
- 🎵 **Audio Support**: Automatic audio extraction and merging
- 🔧 **Flexible Configuration**: Environment-based configuration for easy customization
- 🐳 **Docker Compose**: Simple orchestration with docker-compose
- 📦 **Multi-stage Build**: Optimized Docker image with minimal size
- 🔒 **Security**: Non-root user execution and minimal attack surface
- 🧪 **Testing**: Comprehensive test suite with pytest
- 🤖 **CI/CD**: GitHub Actions for automated testing and releases
- 📚 **Documentation**: Detailed configuration and usage guides

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+ (optional but recommended)
- Git (for cloning)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/vidgear-docker-streamer.git
   cd vidgear-docker-streamer
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   nano .env  # or use your favorite editor
   ```

3. **Create output directory**

   ```bash
   mkdir -p output
   ```

### Usage

#### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t vidgear-streamer .

# Run the container
docker run -v "$(pwd)/output:/app/output" --env-file .env vidgear-streamer

# Run with specific video URL
docker run -v "$(pwd)/output:/app/output" \
  -e VIDEO_URL="https://youtu.be/your-video-id" \
  vidgear-streamer
```

#### Option 3: Using Makefile

```bash
# Build the image
make build

# Run the container
make run

# View logs
make logs

# Clean up
make clean

# Run tests
make test
```

## 📋 Configuration

All configuration is done through environment variables. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed information.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `VIDEO_URL` | Source video URL | `https://youtu.be/xvFZjo5PgG0` |
| `OUTPUT_FILE` | Output file path | `/app/output/vidgear_output.mp4` |
| `VIDEO_STREAM_QUALITY` | Video quality (best/720p/1080p) | `best` |
| `AUDIO_STREAM_QUALITY` | Audio quality | `bestaudio` |
| `OUTPUT_CODEC` | Video codec (libx264/libx265) | `libx264` |
| `AUDIO_CODEC` | Audio codec (aac/mp3) | `aac` |
| `FRAME_LIMIT` | Max frames to process (0=unlimited) | `0` |
| `VERBOSE` | Enable verbose logging | `false` |

## 🧪 Testing

### Run Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_streamer.py::test_streamer_initialization
```

### Run Tests in Docker

```bash
# Using docker-compose
docker-compose -f docker-compose.test.yml up

# Using Makefile
make test
```

## 🔧 Development

### Building from Source

```bash
# Build with default settings
docker build -t vidgear-streamer .

# Build with custom build args
docker build \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  -t vidgear-streamer:dev .
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock

# Run the application locally
python -m app.streamer

# Run tests
pytest
```

## 📖 Examples

### Example 1: Process YouTube Video

```bash
docker run -v "$(pwd)/output:/app/output" \
  -e VIDEO_URL="https://youtu.be/dQw4w9WgXcQ" \
  -e VIDEO_STREAM_QUALITY="720p" \
  -e FRAME_LIMIT="300" \
  vidgear-streamer
```

### Example 2: High-Quality Processing

```bash
docker run -v "$(pwd)/output:/app/output" \
  -e VIDEO_URL="https://youtu.be/your-video" \
  -e VIDEO_STREAM_QUALITY="1080p" \
  -e OUTPUT_CODEC="libx265" \
  -e AUDIO_CODEC="aac" \
  -e VERBOSE="true" \
  vidgear-streamer
```

### Example 3: Quick Test Processing

```bash
docker run -v "$(pwd)/output:/app/output" \
  -e VIDEO_URL="https://youtu.be/test-video" \
  -e FRAME_LIMIT="100" \
  -e VERBOSE="true" \
  vidgear-streamer
```

See [examples/](examples/) directory for more usage examples.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [VidGear](https://github.com/abhiTronix/vidgear) - High-performance video processing framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenCV](https://opencv.org/) - Computer vision library

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/vidgear-docker-streamer/issues)
- 💬 [Discussions](https://github.com/yourusername/vidgear-docker-streamer/discussions)

## 🗺️ Roadmap

- [ ] Add GPU acceleration support (NVIDIA/AMD)
- [ ] Implement real-time streaming (RTMP/HLS)
- [ ] Add web UI for configuration
- [ ] Add video filters and effects
- [ ] Implement batch processing

## ⚠️ Troubleshooting

### Common Issues

#### Issue: Permission denied errors

```bash
# Fix permissions on output directory
chmod -R 755 output/
```

#### Issue: Container exits immediately

```bash
# Check logs
docker-compose logs

# Run with verbose mode
docker-compose up --env VERBOSE=true
```

#### Issue: Video URL not supported

```bash
# Test URL with yt-dlp first
yt-dlp -F "your-video-url"
```

## 📊 Performance

Typical performance metrics:

- **CPU Usage**: 150-400% (multi-core)
- **Memory**: 500MB - 2GB (depends on video quality)
- **Processing Speed**: Real-time to 2x realtime (depends on codec)
- **Disk I/O**: Moderate (depends on output format)

---

Made with ❤️.
