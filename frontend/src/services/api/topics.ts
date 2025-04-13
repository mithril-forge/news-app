/**
 * API services for topic-related operations
 */
import { fetchApi } from '@/services/https';
import { Topic } from '@/types';

/**
 * Fetches all available topics/categories
 * @returns Promise with array of topics
 */
export const fetchTopics = async (): Promise<Topic[]> => {
  return fetchApi<Topic[]>('/topics');
};