import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const WebcamStream = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const receivedCanvasRef = useRef(null);
  const websocketRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const intervalIdRef = useRef(null);
  const navigate = useNavigate();

  const websocketUrl = process.env.REACT_APP_API_BASE_URL+'/ws/process_stream_feed/' || 'ws://localhost:8000/ws/process_stream_feed/';

  const startStreaming = () => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }

        websocketRef.current = new WebSocket(websocketUrl);

        websocketRef.current.onopen = () => {
          console.log('WebSocket connection opened');
          setIsStreaming(true);
        };

        websocketRef.current.onclose = () => {
          console.log('WebSocket connection closed');
          setIsStreaming(false);
        };

        websocketRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        websocketRef.current.onmessage = (event) => {
          console.log('Received message:', event.data);
          const blob = event.data;
          const url = URL.createObjectURL(blob);
          const img = new Image();
          img.onload = () => {
            const context = receivedCanvasRef.current.getContext('2d');
            context.drawImage(img, 0, 0, receivedCanvasRef.current.width, receivedCanvasRef.current.height);
            URL.revokeObjectURL(url);
          };
          img.src = url;
        };

        intervalIdRef.current = setInterval(() => {
          if (videoRef.current && canvasRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            const context = canvasRef.current.getContext('2d');
            context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
            canvasRef.current.toBlob(blob => {
              if (blob) {
                websocketRef.current.send(blob);
                console.log('Sent frame of size:', blob.size);
              }
            }, 'image/jpeg');
          }
        }, 1000 / 30); // Send frames at 30 FPS
      })
      .catch(error => {
        console.error('Error accessing webcam:', error);
      });
  };

  const stopStreaming = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
    }
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    setIsStreaming(false);
  }, [navigate]);

  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, [stopStreaming]);

  return (
    <div>
      <h1>Webcam Stream</h1>
      <div style={{ position: 'fixed', top: 0, width: '100%', backgroundColor: 'white', zIndex: 1 }}>
        {isStreaming ? (
          <button onClick={stopStreaming}>Stop Streaming</button>
        ) : (
          <button onClick={startStreaming}>Start Streaming</button>
        )}
      </div>
      <div style={{ marginTop: '50px' }}>
        <video ref={videoRef} autoPlay style={{ display: 'none' }} />
        <canvas ref={canvasRef} width="640" height="480" style={{ display: isStreaming ? 'block' : 'none' }} />
        <canvas ref={receivedCanvasRef} width="640" height="480" style={{ display: isStreaming ? 'block' : 'none' }} />
      </div>
    </div>
  );
};

export default WebcamStream;