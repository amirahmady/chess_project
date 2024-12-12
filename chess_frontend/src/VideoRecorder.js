import React, { useRef, useState } from 'react';
import { uploadStream, getVideoFeed } from './api';
import { useNavigate } from 'react-router-dom';

const VideoRecorder = () => {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [videoURL, setVideoURL] = useState(null);
  const [processedVideoURL, setProcessedVideoURL] = useState(null);
  const history = useNavigate();

  console.log('VideoRecorder component rendered');

  const startRecording = async () => {
    console.log('startRecording called');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;

    const options = { mimeType: 'video/mp4' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.warn(`${options.mimeType} is not supported, using default mimeType`);
      options.mimeType = '';
    }

    mediaRecorderRef.current = new MediaRecorder(stream, options);

    const chunks = [];
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(chunks, { type: 'video/mp4' });
      const url = URL.createObjectURL(blob);
      setVideoURL(url);
      console.log('Recording stopped, video URL:', url);

      // Upload the video file
      const file = new File([blob], 'video.mp4', { type: 'video/mp4' });
      try {
        const response = await uploadStream(file);
        console.log('Upload response:', response);

        // Fetch the processed video feed
        if (response.video_id) {
          console.log(`Fetching video feed for video ID: ${response.video_id}`);
          const processedVideoUrl = getVideoFeed(response.video_id);
          console.log(`Fetched processed video feed URL: ${processedVideoUrl}`);
          setProcessedVideoURL(processedVideoUrl);
        } else {
          console.error('No video ID returned from upload response');
        }
      } catch (error) {
        console.error('Error uploading stream:', error);
      }
    };

    mediaRecorderRef.current.start();
    setIsRecording(true);
    console.log('Recording started');
  };

  const stopRecording = () => {
    console.log('stopRecording called');
    mediaRecorderRef.current.stop();
    videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    setIsRecording(false);
    console.log('Recording stopped');
  };

  return (
    <div>
      <h1>Video Recorder</h1>
      <div style={{ position: 'fixed', top: 0, width: '100%', backgroundColor: 'white', zIndex: 1 }}>
        {isRecording ? (
          <button onClick={stopRecording}>Stop Recording</button>
        ) : (
          <button onClick={startRecording}>Start Recording</button>
        )}
      </div>
      <div style={{ marginTop: '50px' }}>
        <video ref={videoRef} autoPlay />
        {videoURL && (
          <div>
            <h3>Recorded Video Feed:</h3>
            <video src={videoURL} controls />
          </div>
        )}
        {processedVideoURL && (
          <div>
            <h3>Processed Video Feed:</h3>
            <video src={processedVideoURL} controls />
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoRecorder;