/**
 * API services for news article-related operations
 */
import { fetchApi } from '@/services/https';
import { NewsArticle, NewsDetailed } from '@/types';

/**
 * Fetches all news articles for a specific topic
 * @param topicId - The ID of the topic to fetch news for
 * @returns Promise with array of news articles
 */
export const fetchNewsByTopic = async (topicId: string): Promise<NewsArticle[]> => {
  return fetchApi<NewsArticle[]>(`/news/topics/${topicId}`);
};

/**
 * Fetches the latest news articles
 * @param count - The number of latest articles to retrieve (default: 10)
 * @returns Promise with array of news articles
 */
export const fetchLatestNews = async (count = 10): Promise<NewsArticle[]> => {
  return fetchApi<NewsArticle[]>(`/news/latest?limit=${count}`);
};

/**
 * Fetches a specific news article by ID
 * @param newsId - The ID of the news article to fetch
 * @returns Promise with the news article or null if not found
 */
export const fetchNewsById = async (newsId: string): Promise<NewsDetailed | null> => {
  try {
    return await fetchApi<NewsArticle>(`/news/${newsId}`);
  } catch (error) {
    // Return null instead of throwing for 404 handling
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
    throw error;
  }
};