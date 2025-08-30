/**
 * API services for news article-related operations
 */
import { fetchApi } from '@/services/https';
import { NewsArticle } from '@/types';
import { sort } from "next/dist/build/webpack/loaders/css-loader/src/utils";

/**
 * Fetches all news articles for a specific topic
 * @param topicId - The ID of the topic to fetch news for
 * @param limit - Maximum number of articles to fetch (default: 10)
 * @param offset - Number of articles to skip for pagination (default: 0)
 * @returns Promise with array of news articles
 */
export const fetchNewsByTopic = async (
  topicId: string,
  limit = 10,
  offset = 0
): Promise<NewsArticle[]> => {
  return fetchApi<NewsArticle[]>(
    `/news/topics/${topicId}?limit=${limit}&skip=${offset}`
  );
};

/**
 * Fetches the latest news articles
 * @param limit - The number of latest articles to retrieve (default: 10)
 * @param offset - Number of articles to skip for pagination (default: 0)
 * @param sort_by - Sort by relevance or without the filter
 * @returns Promise with array of news articles
 */
export const fetchLatestNews = async (
  limit = 10,
  offset = 0,
  sort_by = "relevance"
): Promise<NewsArticle[]> => {
  return fetchApi<NewsArticle[]>(
    `/news/latest?limit=${limit}&skip=${offset}&sort_by=${sort_by}`
  );
};

/**
 * Fetches the most popular news articles
 * @param days - Number of days to fetch popular news for
 * @param limit - Number of articles to fetch
 * @returns Promise with array of news articles
 */
export const fetchPopularNews = async (
  days = 7,
  limit = 10
): Promise<NewsArticle[]> => {
  return fetchApi<NewsArticle[]>(
    `/news/popular?days=${days}&limit=${limit}`
  );
};


/**
 * Fetches a specific news article by ID
 * @param newsId - The ID of the news article to fetch
 * @returns Promise with the news article or null if not found
 */
export const fetchNewsById = async (newsId: string): Promise<NewsArticle | null> => {
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