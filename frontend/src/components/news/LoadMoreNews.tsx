'use client'

/**
 * Client component for loading and displaying additional news articles
 * With state reset when category changes
 */
import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { fetchLatestNews, fetchNewsByTopic } from '@/services/api';
import ArticleCard from './ArticleCard';

interface LoadMoreNewsProps {
  /** The active category name */
  activeCategory: string;
  /** The topic ID to fetch more news for (if category-specific) */
  topicId?: string;
  /** Initial count of displayed articles (for pagination) */
  initialCount: number;
}

export default function LoadMoreNews({
  activeCategory,
  topicId,
  initialCount
}: LoadMoreNewsProps) {
  const [additionalArticles, setAdditionalArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  // Number of items to load per page
  const pageSize = 9;

  // Reset state when category or topic changes
  useEffect(() => {
    console.log('Category or topic changed, resetting loaded articles');
    setAdditionalArticles([]);
    setHasMore(true);
    setIsLoading(false);
  }, [activeCategory, topicId]);

  /**
   * Handles loading more news articles
   */
  const handleLoadMore = async () => {
    if (isLoading || !hasMore) return;
    
    setIsLoading(true);
    try {
      // Calculate the current offset
      const currentOffset = initialCount + additionalArticles.length;
      let moreNews;
      
      console.log(`Loading more for: ${activeCategory}, topicId: ${topicId}, offset: ${currentOffset}`);
      
      if (activeCategory === "Vše") {
        moreNews = await fetchLatestNews(pageSize, currentOffset);
      } else if (topicId) {
        moreNews = await fetchNewsByTopic(topicId, pageSize, currentOffset);
      } else {
        setHasMore(false);
        return;
      }
      
      console.log(`Loaded ${moreNews?.length || 0} additional articles`);
      
      // If we received fewer items than requested, we've reached the end
      if (!moreNews || moreNews.length < pageSize) {
        setHasMore(false);
      }
      
      // Add new articles to the local state
      if (moreNews && moreNews.length > 0) {
        setAdditionalArticles(prev => [...prev, ...moreNews]);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error loading more news:', error);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <>
      {/* Additional articles loaded client-side */}
      {additionalArticles.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          {additionalArticles.map(item => (
            <ArticleCard key={item.id} item={item} />
          ))}
        </div>
      )}
      
      {/* Load more button or loading indicator */}
      {hasMore && (
        <div className="mt-8 text-center">
          {isLoading ? (
            <div className="flex justify-center items-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-600"></div>
              <span className="ml-2 text-gray-600">Načítám další články...</span>
            </div>
          ) : (
            <button
              onClick={handleLoadMore}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-colors"
            >
              Načíst další články
            </button>
          )}
        </div>
      )}
    </>
  );
}