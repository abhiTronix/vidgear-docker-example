"""
Copyright 2025 Abhishek Thakur(@abhiTronix) <abhi.una12@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# VidGear Video Streamer with Audio Support

import os
import sys
import signal
import logging as log
import shutil
from pathlib import Path
from yt_dlp import YoutubeDL
from vidgear.gears import CamGear, WriteGear
from vidgear.gears.helper import logger_handler

# Initialize logger
logger = log.getLogger("Video Streamer")
logger.propagate = False
logger.addHandler(logger_handler())
logger.setLevel(log.DEBUG)


class VideoStreamer:
    """Handles Video streaming and video writing with audio support."""

    def __init__(self):
        """Initialize the streamer with environment variables."""
        self.source_url = os.getenv("VIDEO_URL", "https://youtu.be/xvFZjo5PgG0")
        self.output_file = Path(os.getenv("OUTPUT_FILE", "/app/output/vidgear_output.mp4"))
        self.video_stream_quality = os.getenv("VIDEO_STREAM_QUALITY", "best")
        self.audio_stream_quality = os.getenv("AUDIO_STREAM_QUALITY", "bestaudio")
        self.output_codec = os.getenv("OUTPUT_CODEC", "libx264")
        self.audio_codec = os.getenv("AUDIO_CODEC", "aac")
        self.frame_limit = int(os.getenv("FRAME_LIMIT", "0"))  # 0 = no limit
        self.output_video = Path(os.getenv("OUTPUT_VIDEO", "/app/output/vidgear_video.mp4"))
        self.output_audio = Path(os.getenv("OUTPUT_AUDIO", "/app/output/vidgear_audio.aac"))
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"
        self.stream = None
        self.writer = None
        self.frame_count = 0
        self.framerate = 30  # Default framerate

    def _has_audio(self):
        """Check if the source has available audio formats."""
        try:
            logger.info("🔍 Checking for available audio formats...")
            with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(self.source_url, download=False)
                formats = info.get("formats", [])
                for fmt in formats:
                    if fmt.get("audio_ext") not in [None, "none"]:
                        logger.info("✅ Audio format found in source")
                        return True
            return False
        except Exception as e:
            logger.warning(f"⚠️  Could not check for audio formats: {e}")
            return False

    def download_audio(self):
        """Download audio stream using yt-dlp if available."""
        if not self._has_audio():
            logger.info("🎧 No audio format available, skipping audio download")
            return
        ydl_opts = {
            "format": f"{self.audio_stream_quality}",
            "quiet": True,
            "no_warnings": True,
            "outtmpl": self.output_audio.as_posix(),
        }
        logger.info(f"🎧 Downloading audio to: {self.output_audio}")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.source_url])

    def setup_stream(self):
        """Initialize CamGear for Video streaming with audio."""
        logger.info(f"🌐 Initializing stream from: {self.source_url}")
        logger.info(f"📊 Stream quality: {self.video_stream_quality}")

        # CamGear options for Video streaming with yt-dlp
        stream_options = {
            "STREAM_RESOLUTION": self.video_stream_quality,
        }
        try:
            self.stream = CamGear(
                source=self.source_url,
                stream_mode=True,
                logging=self.verbose,
                **stream_options,
            ).start()
            logger.info("✅ Stream initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize stream: {e}")
            raise
        # get Video's metadata as JSON object
        video_metadata = self.stream.ytv_metadata
        _framerate = video_metadata.get("fps", None)
        self.framerate = _framerate if _framerate is not None else 30
        logger.info(f"🎞️  Video framerate detected: {self.framerate} FPS")

    def setup_writer(self):
        """Initialize WriteGear for video writing with audio support."""
        logger.info(f"📝 Setting up video writer: {self.output_video}")

        # Ensure output directory exists
        output_dir = self.output_video.parent
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # WriteGear output parameters for audio support (Compression Mode)
        output_params = {
            "-input_framerate": self.framerate,
            "-c:v": self.output_codec,
        }

        try:
            self.writer = WriteGear(
                output=self.output_video.as_posix(),
                compression_mode=True,
                logging=self.verbose,
                **output_params,
            )
            logger.info("✅ Video writer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize writer: {e}")
            raise

    def process_stream(self):
        """Main processing loop: read frames from stream and write to output."""
        logger.info("🎬 Starting video processing...")
        logger.info(
            f"⏹️  Frame limit: {'Unlimited' if self.frame_limit == 0 else self.frame_limit}"
        )

        try:
            while True:
                # Read frame from stream
                frame = self.stream.read()

                # Check if frame is None (stream ended)
                if frame is None:
                    logger.info("🏁 Stream ended or no more frames available")
                    break

                # Write frame to output
                self.writer.write(frame)
                self.frame_count += 1

                # Progress indicator
                if self.frame_count % 100 == 0:
                    logger.info(f"📊 Processed {self.frame_count} frames...")

                # Check frame limit
                if self.frame_limit > 0 and self.frame_count >= self.frame_limit:
                    logger.info(f"🎯 Reached frame limit of {self.frame_limit}")
                    break

        except KeyboardInterrupt:
            logger.info("\n⚠️  Keyboard interrupt received, stopping gracefully...")
        except Exception as e:
            logger.error(f"❌ Error during processing: {e}")
            raise
        finally:
            logger.info(f"✅ Total frames processed: {self.frame_count}")

    def combine_audio_video(self):
        """Combine audio and video into final output file, or copy video if no audio."""
        logger.info("🔊 Finalizing output...")
        if self.output_audio.exists():
            logger.info("🔊 Audio available, combining audio and video...")
            try:
                # format FFmpeg command to generate `Output_with_audio.mp4` by merging input_audio in above rendered `Output.mp4`
                ffmpeg_command = [
                    "-y",
                    "-i",
                    self.output_video.as_posix(),
                    "-i",
                    self.output_audio.as_posix(),
                    "-c:v",
                    "copy",
                    "-c:a",
                    "copy",
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-shortest",
                    self.output_file.as_posix(),
                ]  # `-y` parameter is to overwrite outputfile if exists

                # execute FFmpeg command
                self.writer.execute_ffmpeg_cmd(ffmpeg_command)
                logger.info(f"✅ Final output with audio saved to: {self.output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to combine audio and video: {e}")
                raise
        else:
            logger.info("🔊 No audio available, copying video to final output...")
            try:
                shutil.copy2(self.output_video, self.output_file)
                logger.info(f"✅ Final output (video only) saved to: {self.output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to copy video to final output: {e}")
                raise

    def stop(self):
        """Stop the stream and writer."""
        logger.info("🛑 Stopping stream and writer...")
        if self.stream is not None:
            self.stream.stop()
            logger.info("✅ Stream stopped")

        if self.writer is not None:
            self.writer.close()
            logger.info("✅ Writer closed")

    def cleanup(self):
        """Clean up resources."""
        logger.info("🧹 Cleaning up resources...")

        # Ensure everything is stopped
        self.stop()

        # Check if output file was created
        if self.output_file.exists():
            file_size = self.output_file.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"📦 Output file created: {self.output_file}")
            logger.info(f"📏 File size: {file_size:.2f} MB")
        else:
            logger.warning("⚠️  Output file was not created")

        if self.output_audio is not None:
            self.output_audio.unlink(missing_ok=True)
            logger.info(f"🗑️  Temporary audio file removed: {self.output_audio}")
            self.output_audio = None
        if self.output_video is not None:
            self.output_video.unlink(missing_ok=True)
            logger.info(f"🗑️  Temporary video file removed: {self.output_video}")
            self.output_video = None

    def run(self):
        """Main execution method."""
        logger.info("=" * 60)
        logger.info("🎥 VidGear - Video Streamer and Writer")
        logger.info("=" * 60)

        try:
            self.setup_stream()
            self.download_audio()
            self.setup_writer()
            self.process_stream()
            self.stop()  # Ensure everything is stopped before combining
            self.combine_audio_video()
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            sys.exit(1)
        finally:
            self.cleanup()

        logger.info("=" * 60)
        logger.info("🎉 Processing completed successfully!")
        logger.info("=" * 60)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("\n⚠️  Shutdown signal received, exiting...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the streamer
    streamer = VideoStreamer()
    streamer.run()
