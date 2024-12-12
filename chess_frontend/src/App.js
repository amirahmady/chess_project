import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import VideoRecorder from './VideoRecorder';
import WebcamStream from './WebcamStream';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/live_stream" />} />
        <Route path="/live_stream" element={<WebcamStream />} />
        <Route path="/video_recorder" element={<VideoRecorder />} />
      </Routes>
    </Router>
  );
};

export default App;