const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const fetchTopics = async () => {
  try {
    const response = await fetch(`http://0.0.0.0:8000/topics`);
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching topics:', error);
    throw error;
  }
};

export const fetchNewsByTopic = async (topicId) => {
  try {
    const response = await fetch(`http://0.0.0.0:8000/news/topics/${topicId}`);
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching news for topic ${topicId}:`, error);
    throw error;
  }
};

export const fetchLatestNews = async (count = 10) => {
  try {
    const response = await fetch(`http://0.0.0.0:8000/news/latest?limit=${count}`);
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching latest news:', error);
    throw error;
  }
};

export const fetchNewsById = async (newsId) => {
  console.log("Fectching article")
  try {
    const response = await fetch(`http://0.0.0.0:8000/news/${newsId}`);
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching news with ID ${newsId}:`, error);
    throw error;
  }
};