// src/api.js
const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const uploadStream = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${apiBaseUrl}/upload_video/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to upload stream:', error);
    throw error;
  }
};

export const getVideoFeed = (videoId) => {
  console.log(`Requesting video feed for video ID: ${videoId}`);
  const videoFeedUrl = `${apiBaseUrl}/video_feed/?video_id=${videoId}`;
  console.log(`Video feed URL: ${videoFeedUrl}`);
  return videoFeedUrl;
};

export const getRoiData = async (videoId) => {
  try {
    const response = await fetch(`${apiBaseUrl}/roi_data/?video_id=${videoId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch ROI data:', error);
    throw error;
  }
};