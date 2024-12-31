import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import json
from video_processing_service.service.main import process_video, separate_audio_video, handle_message

@patch("video_processing_service.service.main.get_video_resolution")
@patch("video_processing_service.service.main.should_process_resolution")
@patch("subprocess.run")
def test_process_video(mock_subprocess, mock_should_process, mock_get_video_resolution):
    # Arrange: Mock the dependencies
    mock_get_video_resolution.return_value = (1920, 1080)  # Mocked input resolution (1080p)
    
    # Mock should_process_resolution to return True for resolutions it should process
    mock_should_process.side_effect = lambda input_res, target_res: input_res >= tuple(map(int, target_res.split('x')))

    # Create temporary user_id and video_id
    user_id = "1234"
    video_id = "abcd"
    video_path = "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_video.mp4"  # Mock path

    # Mock subprocess.run to avoid actually running ffmpeg commands
    mock_subprocess.return_value = MagicMock()

    # Act: Call the process_video method
    process_video(video_path, user_id, video_id)

    # Assert: Verify get_video_resolution was called once with the correct video path
    mock_get_video_resolution.assert_called_once_with(video_path)

    # Define expected resolutions
    resolutions = [("360p", "640x360"), ("480p", "854x480"), ("720p", "1280x720")]
    
    # Assert: Verify should_process_resolution is called for each resolution
    expected_resolution_calls = [
        call((1920, 1080), "640x360"),
        call((1920, 1080), "854x480"),
        call((1920, 1080), "1280x720")
    ]
    mock_should_process.assert_has_calls(expected_resolution_calls, any_order=True)

    # Assert: Verify subprocess.run was called to create the expected resolutions
    expected_calls = []
    for res_name, res_dim in resolutions:
        scale_filter = (
            f"scale=w='if(gt(iw,{res_dim.split('x')[0]}),{res_dim.split('x')[0]},iw)':"
            f"h='if(gt(ih,{res_dim.split('x')[1]}),{res_dim.split('x')[1]},ih)'"
        )
        output_path = Path(f"{user_id}/vid/{video_id}/video/{res_name}/{res_name}.mp4")
        expected_calls.append(call([ 
            "ffmpeg", "-i", video_path, "-vf", scale_filter, "-c:v", "libx264", 
            "-crf", "23", "-preset", "fast", str(output_path)
        ], check=True))

    mock_subprocess.assert_has_calls(expected_calls, any_order=True)


@patch("subprocess.run")
def test_separate_audio_video(mock_subprocess):
    # Arrange: Define input and output paths
    input_video_path = "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_video.mp4"  # Mock path
    output_video_path = "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_video_no_audio.mp4"  # Mock path
    output_audio_path = "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_audio.mp3"  # Mock path

    # Mock subprocess.run to avoid actually running ffmpeg commands
    mock_subprocess.return_value = MagicMock()

    # Act: Call the separate_audio_video method
    separate_audio_video(input_video_path, output_video_path, output_audio_path)

    # Assert: Verify subprocess.run was called with the correct commands
    expected_audio_command = [
        "ffmpeg", "-i", input_video_path, "-q:a", "0", "-map", "a", output_audio_path
    ]
    expected_video_command = [
        "ffmpeg", "-i", input_video_path, "-an", output_video_path
    ]

    mock_subprocess.assert_has_calls([
        call(expected_audio_command, check=True),
        call(expected_video_command, check=True)
    ])

@patch("video_processing_service.service.main.push_audio_to_service")
@patch("video_processing_service.service.main.process_video")
@patch("video_processing_service.service.main.separate_audio_video")
@patch("video_processing_service.service.main.logger")
def test_handle_message(
    mock_logger,
    mock_separate_audio_video,
    mock_process_video,
    mock_push_audio_to_service,
):
    # Arrange: Mock the logger and other methods
    mock_channel = MagicMock()
    mock_channel.basic_ack = MagicMock()
    mock_separate_audio_video.return_value = None
    mock_process_video.return_value = None
    mock_push_audio_to_service.return_value = None

    # Mock method with a delivery_tag
    mock_method = MagicMock()
    mock_method.delivery_tag = "some_delivery_tag"

    # Create a mock message as a JSON string
    mock_message = json.dumps({
        "user_id": "1234",
        "video_id": "abcd",
        "video_path": "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_video.mp4",  # Mock path
    })

    # Act: Call the handle_message method with the correct number of parameters
    handle_message(mock_channel, mock_method, None, mock_message)

    # Assert: Verify that separate_audio_video was called with the correct parameters
    mock_separate_audio_video.assert_called_once_with(
        "N:/UCD/DISTRIBUTED COMPUTING/Final/comp41720-group-project/video_processing_service/service/mock_video.mp4",
        "1234/vid/abcd/video/video_no_audio.mp4",
        "1234/vid/abcd/audio/audio.mp3"
    )

    # Assert: Verify that process_video was called with the correct parameters
    mock_process_video.assert_called_once_with("1234/vid/abcd/video/video_no_audio.mp4", "1234", "abcd")

    # Assert: Verify that push_audio_to_service was called with the correct parameters
    mock_push_audio_to_service.assert_called_once_with("1234/vid/abcd/audio/audio.mp3", "1234", "abcd")

    # Assert: Verify that basic_ack was called
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)

    # Assert: Verify that the logger was called with the success message
    mock_logger.info.assert_called_once_with("Successfully processed video abcd for user 1234.")