# Configuration Guide

This document provides detailed information about configuring the VidGear Docker Streamer.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Video Source Configuration](#video-source-configuration)
- [Output Configuration](#output-configuration)
- [Quality Settings](#quality-settings)
- [Codec Options](#codec-options)
- [Processing Limits](#processing-limits)
- [Advanced Configuration](#advanced-configuration)
- [Examples](#examples)

## Environment Variables

All configuration is done through environment variables. You can set these in:

1. **`.env` file** (recommended for docker-compose)
2. **Command line** using `-e` flag
3. **docker-compose.yml** in the `environment` section

### Creating Configuration File

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

## Video Source Configuration

### VIDEO_URL

**Type:** String  
**Required:** No  
**Default:** `https://youtu.be/xvFZjo5PgG0`

The URL of the video to stream and process. Supports any platform compatible with yt-dlp, including:

- YouTube (youtu.be, youtube.com)
- Twitch
- Vimeo
- Facebook
- Twitter/X
- TikTok
- And many more...

**Examples:**

```bash
# YouTube video
VIDEO_URL=https://youtu.be/dQw4w9WgXcQ

# YouTube playlist (will process first video)
VIDEO_URL=https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf

# Twitch stream
VIDEO_URL=https://www.twitch.tv/username

# Direct video URL
VIDEO_URL=https://example.com/video.mp4
```

## Output Configuration

### OUTPUT_FILE

**Type:** String  
**Required:** No  
**Default:** `/app/output/vidgear_output.mp4`

Path to the final output file (with audio merged).

**Examples:**

```bash
OUTPUT_FILE=/app/output/my_video.mp4
OUTPUT_FILE=/app/output/videos/processed_$(date +%Y%m%d).mp4
```

### OUTPUT_VIDEO

**Type:** String  
**Required:** No  
**Default:** `/app/output/vidgear_video.mp4`

Temporary video-only output path (will be deleted after processing).

### OUTPUT_AUDIO

**Type:** String  
**Required:** No  
**Default:** `/app/output/vidgear_audio.aac`

Temporary audio-only output path (will be deleted after processing).

## Quality Settings

### VIDEO_STREAM_QUALITY

**Type:** String  
**Required:** No  
**Default:** `best`

Controls the video quality/format to download and process.

**Predefined Options:**

| Value | Description |
|-------|-------------|
| `best` | Highest quality available (video+audio) |
| `worst` | Lowest quality available |
| `bestvideo` | Best video-only stream |
| `worstvideo` | Worst video-only stream |

**Resolution Options:**

| Value | Resolution |
|-------|------------|
| `2160p` | 4K (3840x2160) |
| `1440p` | 2K (2560x1440) |
| `1080p` | Full HD (1920x1080) |
| `720p` | HD (1280x720) |
| `480p` | SD (854x480) |
| `360p` | Low (640x360) |

**Advanced Format Strings:**

```bash
# Best video with height ≤ 720p
VIDEO_STREAM_QUALITY="bestvideo[height<=720]"

# Best video with specific codec
VIDEO_STREAM_QUALITY="bestvideo[vcodec=vp9]"

# Specific bitrate range
VIDEO_STREAM_QUALITY="bestvideo[tbr>=1000][tbr<=2000]"

# Prefer MP4 format
VIDEO_STREAM_QUALITY="bestvideo[ext=mp4]"
```

For more format options, see [yt-dlp format selection](https://github.com/yt-dlp/yt-dlp#format-selection).

### AUDIO_STREAM_QUALITY

**Type:** String  
**Required:** No  
**Default:** `bestaudio`

Controls the audio quality/format.

**Options:**

| Value | Description |
|-------|-------------|
| `bestaudio` | Highest quality audio |
| `worstaudio` | Lowest quality audio |

**Advanced Examples:**

```bash
# Best audio in AAC format
AUDIO_STREAM_QUALITY="bestaudio[acodec=aac]"

# Audio with specific bitrate
AUDIO_STREAM_QUALITY="bestaudio[abr>=128]"

# Prefer M4A format
AUDIO_STREAM_QUALITY="bestaudio[ext=m4a]"
```

## Codec Options

### OUTPUT_CODEC

**Type:** String  
**Required:** No  
**Default:** `libx264`

Video codec for the output file.

**Popular Options:**

| Codec | Description | Quality | Speed | File Size |
|-------|-------------|---------|-------|-----------|
| `libx264` | H.264 (AVC) | Good | Fast | Medium |
| `libx265` | H.265 (HEVC) | Better | Slow | Small |
| `libvpx-vp9` | VP9 | Good | Medium | Small |
| `libvpx` | VP8 | OK | Fast | Medium |
| `mpeg4` | MPEG-4 | OK | Fast | Large |

**Examples:**

```bash
# High compression, slower encoding
OUTPUT_CODEC=libx265

# Fast encoding, good compatibility
OUTPUT_CODEC=libx264

# WebM format
OUTPUT_CODEC=libvpx-vp9
```

### AUDIO_CODEC

**Type:** String  
**Required:** No  
**Default:** `aac`

Audio codec for the output file.

**Options:**

| Codec | Description | Quality | Compatibility |
|-------|-------------|---------|---------------|
| `aac` | AAC | Excellent | Very High |
| `mp3` | MP3 | Good | Very High |
| `opus` | Opus | Excellent | Medium |
| `vorbis` | Vorbis | Good | Medium |
| `flac` | FLAC | Lossless | Medium |

## Processing Limits

### FRAME_LIMIT

**Type:** Integer  
**Required:** No  
**Default:** `0` (unlimited)

Maximum number of frames to process. Useful for:

- Testing the setup
- Creating short clips
- Limiting resource usage
- Processing samples

**Examples:**

```bash
# Process first 10 seconds at 30fps
FRAME_LIMIT=300

# Process first minute at 60fps
FRAME_LIMIT=3600

# Unlimited processing
FRAME_LIMIT=0
```

**Calculating Frame Limits:**

```
frames = duration_seconds × fps

Examples:
- 5 seconds at 30fps = 150 frames
- 10 seconds at 60fps = 600 frames
- 1 minute at 30fps = 1800 frames
```

## Logging Configuration

### VERBOSE

**Type:** Boolean  
**Required:** No  
**Default:** `false`

Enable verbose logging for debugging.

**Values:**

- `true` - Detailed logging including FFmpeg output
- `false` - Normal logging

**Example:**

```bash
# Enable verbose mode
VERBOSE=true
```

## Advanced Configuration

### Custom FFmpeg Options

While not directly configurable through environment variables, you can modify the `streamer.py` file to add custom FFmpeg options.

**Example modifications:**

```python
# In setup_writer method
output_params = {
    "-input_framerate": self.framerate,
    "-c:v": self.output_codec,
    "-preset": "medium",  # Add encoding preset
    "-crf": "23",         # Add quality factor
    "-b:a": "192k",       # Add audio bitrate
}
```

### Resource Limits

You can limit resource usage in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '2.0'
      memory: 2G
```

## Examples

### Example 1: High Quality Processing

```bash
VIDEO_URL=https://youtu.be/your-video
VIDEO_STREAM_QUALITY=1080p
AUDIO_STREAM_QUALITY=bestaudio
OUTPUT_CODEC=libx265
AUDIO_CODEC=aac
FRAME_LIMIT=0
OUTPUT_FILE=/app/output/high_quality.mp4
VERBOSE=true
```

### Example 2: Quick Test

```bash
VIDEO_URL=https://youtu.be/test-video
VIDEO_STREAM_QUALITY=480p
FRAME_LIMIT=100
OUTPUT_FILE=/app/output/test.mp4
VERBOSE=true
```

### Example 3: Live Stream Recording

```bash
VIDEO_URL=https://www.twitch.tv/username
VIDEO_STREAM_QUALITY=best
AUDIO_STREAM_QUALITY=bestaudio
OUTPUT_CODEC=libx264
FRAME_LIMIT=9000  # 5 minutes at 30fps
OUTPUT_FILE=/app/output/stream_$(date +%Y%m%d_%H%M%S).mp4
```

### Example 4: Batch Processing

Create multiple `.env` files:

```bash
# .env.video1
VIDEO_URL=https://youtu.be/video1
OUTPUT_FILE=/app/output/video1.mp4

# .env.video2
VIDEO_URL=https://youtu.be/video2
OUTPUT_FILE=/app/output/video2.mp4
```

Run with:

```bash
docker-compose --env-file .env.video1 up
docker-compose --env-file .env.video2 up
```

## Validation

To validate your configuration:

```bash
# Check environment variables
make check-env

# Test with a short clip
FRAME_LIMIT=100 make run

# View logs
make logs
```

## Troubleshooting

### Common Issues

**Issue:** Video URL not supported  
**Solution:** Test with yt-dlp first: `yt-dlp -F "your-url"`

**Issue:** Output file not created  
**Solution:** Check permissions on output directory and enable verbose mode

**Issue:** Poor quality output  
**Solution:** Increase VIDEO_STREAM_QUALITY or change OUTPUT_CODEC

**Issue:** Slow processing  
**Solution:** Use faster codec (libx264) or lower quality settings

## Best Practices

1. **Start with defaults** - Use default settings first, then optimize
2. **Test with FRAME_LIMIT** - Always test with a small frame limit first
3. **Enable VERBOSE** - Use verbose mode when troubleshooting
4. **Match codecs** - Use compatible video and audio codecs
5. **Monitor resources** - Watch CPU and memory usage during processing
6. **Validate URLs** - Check URLs with yt-dlp before processing
7. **Backup configs** - Keep multiple .env files for different scenarios

## Reference Links

- [yt-dlp Format Selection](https://github.com/yt-dlp/yt-dlp#format-selection)
- [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html)
- [VidGear Documentation](https://abhitronix.github.io/vidgear/)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
