#!/usr/bin/env python3
"""
VidGear Video Streamer - Basic Usage Examples

This file demonstrates how to use the VideoStreamer class programmatically.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.streamer import VideoStreamer


def example_basic_usage():
    """
    Example 1: Basic usage with default settings
    """
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Set environment variables
    os.environ["VIDEO_URL"] = "https://youtu.be/xvFZjo5PgG0"
    os.environ["OUTPUT_FILE"] = "/tmp/output_basic.mp4"
    os.environ["FRAME_LIMIT"] = "300"  # Process only 300 frames (~10 seconds at 30fps)
    os.environ["VERBOSE"] = "true"
    
    # Create and run streamer
    streamer = VideoStreamer()
    streamer.run()
    
    print("\n✅ Example 1 completed!")


def example_custom_quality():
    """
    Example 2: Custom quality settings
    """
    print("\n" + "=" * 60)
    print("Example 2: Custom Quality Settings")
    print("=" * 60)
    
    # Configure for 720p video with high quality audio
    os.environ["VIDEO_URL"] = "https://youtu.be/xvFZjo5PgG0"
    os.environ["OUTPUT_FILE"] = "/tmp/output_720p.mp4"
    os.environ["VIDEO_STREAM_QUALITY"] = "720p"
    os.environ["AUDIO_STREAM_QUALITY"] = "bestaudio"
    os.environ["FRAME_LIMIT"] = "150"
    os.environ["VERBOSE"] = "true"
    
    streamer = VideoStreamer()
    streamer.run()
    
    print("\n✅ Example 2 completed!")


def example_custom_codec():
    """
    Example 3: Custom codec settings
    """
    print("\n" + "=" * 60)
    print("Example 3: Custom Codec Settings")
    print("=" * 60)
    
    # Use H.265 codec for better compression
    os.environ["VIDEO_URL"] = "https://youtu.be/xvFZjo5PgG0"
    os.environ["OUTPUT_FILE"] = "/tmp/output_h265.mp4"
    os.environ["OUTPUT_CODEC"] = "libx265"
    os.environ["AUDIO_CODEC"] = "aac"
    os.environ["FRAME_LIMIT"] = "200"
    os.environ["VERBOSE"] = "false"
    
    streamer = VideoStreamer()
    streamer.run()
    
    print("\n✅ Example 3 completed!")


def example_programmatic_override():
    """
    Example 4: Programmatic configuration override
    """
    print("\n" + "=" * 60)
    print("Example 4: Programmatic Override")
    print("=" * 60)
    
    # Set base environment
    os.environ["VIDEO_URL"] = "https://youtu.be/xvFZjo5PgG0"
    os.environ["FRAME_LIMIT"] = "100"
    
    # Create streamer and override settings
    streamer = VideoStreamer()
    
    # Override settings programmatically
    streamer.output_file = "/tmp/output_programmatic.mp4"
    streamer.video_stream_quality = "480p"
    streamer.output_codec = "libx264"
    streamer.verbose = True
    
    print(f"Processing {streamer.frame_limit} frames")
    print(f"Output: {streamer.output_file}")
    print(f"Quality: {streamer.video_stream_quality}")
    
    streamer.run()
    
    print("\n✅ Example 4 completed!")


def example_error_handling():
    """
    Example 5: Error handling
    """
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    try:
        # Try to process an invalid URL
        os.environ["VIDEO_URL"] = "https://invalid-url-example.com/nonexistent"
        os.environ["OUTPUT_FILE"] = "/tmp/output_error.mp4"
        os.environ["FRAME_LIMIT"] = "50"
        
        streamer = VideoStreamer()
        streamer.run()
        
    except Exception as e:
        print(f"❌ Error caught: {e}")
        print("This is expected when using an invalid URL")
    
    print("\n✅ Example 5 completed (error handled)!")


def example_conditional_processing():
    """
    Example 6: Conditional processing based on video metadata
    """
    print("\n" + "=" * 60)
    print("Example 6: Conditional Processing")
    print("=" * 60)
    
    os.environ["VIDEO_URL"] = "https://youtu.be/xvFZjo5PgG0"
    os.environ["FRAME_LIMIT"] = "0"  # No limit
    
    streamer = VideoStreamer()
    
    # Setup stream to get metadata
    streamer.setup_stream()
    
    # Check framerate and adjust settings
    if streamer.framerate >= 60:
        print(f"High framerate detected: {streamer.framerate} fps")
        print("Adjusting frame limit for performance...")
        streamer.frame_limit = 600  # 10 seconds at 60fps
    else:
        print(f"Normal framerate: {streamer.framerate} fps")
        streamer.frame_limit = 300  # 10 seconds at 30fps
    
    streamer.output_file = "/tmp/output_conditional.mp4"
    
    # Continue with processing
    streamer.setup_writer()
    streamer.process_stream()
    streamer.stop()
    streamer.combine_audio_video()
    streamer.cleanup()
    
    print("\n✅ Example 6 completed!")


def main():
    """
    Run all examples (or specific ones)
    """
    examples = {
        "1": ("Basic Usage", example_basic_usage),
        "2": ("Custom Quality", example_custom_quality),
        "3": ("Custom Codec", example_custom_codec),
        "4": ("Programmatic Override", example_programmatic_override),
        "5": ("Error Handling", example_error_handling),
        "6": ("Conditional Processing", example_conditional_processing),
    }
    
    print("\n🎥 VidGear Video Streamer - Usage Examples")
    print("=" * 60)
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  all. Run all examples")
    print("  q. Quit")
    
    choice = input("\nSelect an example to run (1-6, all, or q): ").strip().lower()
    
    if choice == "q":
        print("Goodbye!")
        return
    elif choice == "all":
        for name, func in examples.values():
            try:
                func()
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                continue
    elif choice in examples:
        try:
            examples[choice][1]()
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("❌ Invalid choice")
        return
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Exiting...")
        sys.exit(0)
