"""
Pytest configuration and fixtures for VidGear Streamer tests
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_env_vars(monkeypatch):
    """Set up test environment variables"""
    test_vars = {
        "VIDEO_URL": "https://youtu.be/xvFZjo5PgG0",
        "OUTPUT_FILE": "/tmp/test_output.mp4",
        "VIDEO_STREAM_QUALITY": "best",
        "AUDIO_STREAM_QUALITY": "bestaudio",
        "OUTPUT_CODEC": "libx264",
        "AUDIO_CODEC": "aac",
        "FRAME_LIMIT": "10",  # Low limit for testing
        "OUTPUT_VIDEO": "/tmp/test_video.mp4",
        "OUTPUT_AUDIO": "/tmp/test_audio.aac",
        "VERBOSE": "false",
    }
    
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    
    return test_vars


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory"""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def cleanup_files():
    """Clean up test files after tests"""
    files_to_cleanup = []
    
    def register_file(filepath):
        files_to_cleanup.append(filepath)
    
    yield register_file
    
    # Cleanup
    for filepath in files_to_cleanup:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass


@pytest.fixture
def mock_stream():
    """Mock CamGear stream for testing"""
    from unittest.mock import Mock
    
    stream = Mock()
    stream.read.return_value = None  # Simulate end of stream
    stream.ytv_metadata = {"fps": 30}
    stream.stop = Mock()
    
    return stream


@pytest.fixture
def mock_writer():
    """Mock WriteGear writer for testing"""
    from unittest.mock import Mock
    
    writer = Mock()
    writer.write = Mock()
    writer.close = Mock()
    writer.execute_ffmpeg_cmd = Mock()
    
    return writer
