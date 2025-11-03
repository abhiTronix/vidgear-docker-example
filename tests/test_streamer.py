"""
Unit tests for VidGear Video Streamer
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.streamer import VideoStreamer


class TestVideoStreamerInitialization:
    """Test VideoStreamer initialization"""
    
    def test_streamer_initialization(self, test_env_vars):
        """Test that VideoStreamer initializes with correct environment variables"""
        with patch('app.streamer.VideoStreamer.download_audio'):
            streamer = VideoStreamer()
            
            assert streamer.source_url == test_env_vars["VIDEO_URL"]
            assert streamer.output_file == test_env_vars["OUTPUT_FILE"]
            assert streamer.video_stream_quality == test_env_vars["VIDEO_STREAM_QUALITY"]
            assert streamer.audio_stream_quality == test_env_vars["AUDIO_STREAM_QUALITY"]
            assert streamer.output_codec == test_env_vars["OUTPUT_CODEC"]
            assert streamer.audio_codec == test_env_vars["AUDIO_CODEC"]
            assert streamer.frame_limit == int(test_env_vars["FRAME_LIMIT"])
            assert streamer.verbose == False
    
    def test_default_values(self, monkeypatch):
        """Test default values when environment variables are not set"""
        # Clear all environment variables
        for key in ["VIDEO_URL", "OUTPUT_FILE", "VIDEO_STREAM_QUALITY", 
                    "AUDIO_STREAM_QUALITY", "OUTPUT_CODEC", "AUDIO_CODEC",
                    "FRAME_LIMIT", "VERBOSE"]:
            monkeypatch.delenv(key, raising=False)
        
        with patch('app.streamer.VideoStreamer.download_audio'):
            streamer = VideoStreamer()
            
            assert streamer.source_url == "https://youtu.be/xvFZjo5PgG0"
            assert streamer.output_file == "/app/output/vidgear_output.mp4"
            assert streamer.video_stream_quality == "best"
            assert streamer.audio_stream_quality == "bestaudio"
            assert streamer.output_codec == "libx264"
            assert streamer.audio_codec == "aac"
            assert streamer.frame_limit == 0
            assert streamer.verbose == False


class TestVideoStreamerDownload:
    """Test audio download functionality"""
    
    @patch('app.streamer.YoutubeDL')
    def test_download_audio(self, mock_ytdl, test_env_vars):
        """Test audio download with yt-dlp"""
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        streamer = VideoStreamer()
        
        # Verify YoutubeDL was called with correct options
        mock_ytdl.assert_called_once()
        call_args = mock_ytdl.call_args[0][0]
        
        assert call_args["format"] == test_env_vars["AUDIO_STREAM_QUALITY"]
        assert call_args["quiet"] == True
        assert call_args["no_warnings"] == True
        assert call_args["outtmpl"] == test_env_vars["OUTPUT_AUDIO"]
        
        # Verify download was called
        mock_ytdl_instance.download.assert_called_once_with([test_env_vars["VIDEO_URL"]])


class TestVideoStreamerSetup:
    """Test stream and writer setup"""
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('app.streamer.CamGear')
    def test_setup_stream(self, mock_camgear, mock_download):
        """Test stream initialization"""
        mock_stream = Mock()
        mock_stream.ytv_metadata = {"fps": 30}
        mock_camgear.return_value.start.return_value = mock_stream
        
        streamer = VideoStreamer()
        streamer.setup_stream()
        
        assert streamer.stream == mock_stream
        assert streamer.framerate == 30
        mock_camgear.assert_called_once()
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('app.streamer.WriteGear')
    @patch('app.streamer.Path')
    def test_setup_writer(self, mock_path, mock_writegear, mock_download):
        """Test writer initialization"""
        mock_writer = Mock()
        mock_writegear.return_value = mock_writer
        
        streamer = VideoStreamer()
        streamer.framerate = 30
        streamer.setup_writer()
        
        assert streamer.writer == mock_writer
        mock_writegear.assert_called_once()
        
        # Verify output parameters
        call_kwargs = mock_writegear.call_args[1]
        assert call_kwargs["compression_mode"] == True


class TestVideoStreamerProcessing:
    """Test video processing functionality"""
    
    @patch('app.streamer.VideoStreamer.download_audio')
    def test_process_stream_no_frames(self, mock_download, mock_stream, mock_writer):
        """Test processing when stream has no frames"""
        streamer = VideoStreamer()
        streamer.stream = mock_stream
        streamer.writer = mock_writer
        streamer.frame_limit = 0
        
        # Stream returns None immediately (no frames)
        mock_stream.read.return_value = None
        
        streamer.process_stream()
        
        assert streamer.frame_count == 0
        mock_writer.write.assert_not_called()
    
    @patch('app.streamer.VideoStreamer.download_audio')
    def test_process_stream_with_frames(self, mock_download, mock_writer):
        """Test processing with actual frames"""
        import numpy as np
        
        streamer = VideoStreamer()
        
        # Create mock stream that returns 5 frames then None
        mock_stream = Mock()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_stream.read.side_effect = [frame] * 5 + [None]
        
        streamer.stream = mock_stream
        streamer.writer = mock_writer
        streamer.frame_limit = 0  # No limit
        
        streamer.process_stream()
        
        assert streamer.frame_count == 5
        assert mock_writer.write.call_count == 5
    
    @patch('app.streamer.VideoStreamer.download_audio')
    def test_process_stream_with_limit(self, mock_download, mock_writer):
        """Test processing with frame limit"""
        import numpy as np
        
        streamer = VideoStreamer()
        
        # Create mock stream that would return many frames
        mock_stream = Mock()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_stream.read.return_value = frame
        
        streamer.stream = mock_stream
        streamer.writer = mock_writer
        streamer.frame_limit = 10
        
        streamer.process_stream()
        
        assert streamer.frame_count == 10
        assert mock_writer.write.call_count == 10


class TestVideoStreamerCleanup:
    """Test cleanup functionality"""
    
    @patch('app.streamer.VideoStreamer.download_audio')
    def test_stop(self, mock_download, mock_stream, mock_writer):
        """Test stopping stream and writer"""
        streamer = VideoStreamer()
        streamer.stream = mock_stream
        streamer.writer = mock_writer
        
        streamer.stop()
        
        mock_stream.stop.assert_called_once()
        mock_writer.close.assert_called_once()
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.remove')
    def test_cleanup_with_files(self, mock_remove, mock_getsize, mock_exists, mock_download):
        """Test cleanup when output files exist"""
        streamer = VideoStreamer()
        streamer.stream = Mock()
        streamer.writer = Mock()
        
        # Mock file existence
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1 MB
        
        streamer.cleanup()
        
        # Verify files were removed
        assert mock_remove.call_count >= 2  # audio and video files


class TestVideoStreamerCombine:
    """Test audio-video combination"""
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('os.path.exists')
    def test_combine_audio_video(self, mock_exists, mock_download, mock_writer):
        """Test combining audio and video"""
        streamer = VideoStreamer()
        streamer.writer = mock_writer
        mock_exists.return_value = True
        
        streamer.combine_audio_video()
        
        # Verify FFmpeg command was executed
        mock_writer.execute_ffmpeg_cmd.assert_called_once()
        
        # Verify command structure
        call_args = mock_writer.execute_ffmpeg_cmd.call_args[0][0]
        assert "-y" in call_args
        assert "-i" in call_args
        assert "-c:v" in call_args
        assert "copy" in call_args
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('os.path.exists')
    def test_combine_audio_video_no_audio(self, mock_exists, mock_download, mock_writer):
        """Test combining when audio file doesn't exist"""
        streamer = VideoStreamer()
        streamer.writer = mock_writer
        mock_exists.return_value = False
        
        streamer.combine_audio_video()
        
        # Should not execute FFmpeg when audio is missing
        mock_writer.execute_ffmpeg_cmd.assert_not_called()


class TestVideoStreamerIntegration:
    """Integration tests"""
    
    @patch('app.streamer.VideoStreamer.download_audio')
    @patch('app.streamer.VideoStreamer.setup_stream')
    @patch('app.streamer.VideoStreamer.setup_writer')
    @patch('app.streamer.VideoStreamer.process_stream')
    @patch('app.streamer.VideoStreamer.stop')
    @patch('app.streamer.VideoStreamer.combine_audio_video')
    @patch('app.streamer.VideoStreamer.cleanup')
    def test_run_method(self, mock_cleanup, mock_combine, mock_stop, 
                       mock_process, mock_setup_writer, mock_setup_stream, 
                       mock_download):
        """Test the main run method"""
        streamer = VideoStreamer()
        streamer.run()
        
        # Verify all methods were called in order
        mock_setup_stream.assert_called_once()
        mock_setup_writer.assert_called_once()
        mock_process.assert_called_once()
        mock_stop.assert_called_once()
        mock_combine.assert_called_once()
        mock_cleanup.assert_called_once()


def test_import():
    """Test that the module can be imported"""
    from app import streamer
    assert hasattr(streamer, 'VideoStreamer')


def test_module_attributes():
    """Test module has expected attributes"""
    from app import streamer
    
    assert hasattr(streamer, 'VideoStreamer')
    assert hasattr(streamer, 'signal_handler')
    assert hasattr(streamer, 'logger')
