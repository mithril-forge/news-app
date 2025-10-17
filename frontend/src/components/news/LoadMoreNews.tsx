'use client'

import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { fetchLatestNews, fetchNewsByTopic } from '@/services/api';
import { SortOption } from '@/components/common/SortDropdown';
import { Button } from '~/components/ui/button';
import { Loader2 } from 'lucide-react';
import ArticleCard from './ArticleCard';

interface LoadMoreNewsProps {
  /** The active category name */
  activeCategory: string;
  /** The topic ID to fetch more news for (if category-specific) */
  topicId?: string;
  /** Initial count of displayed articles (for pagination) */
  initialCount: number;
  /** Current sort option - only used for main page */
  sortBy?: SortOption;
}

export default function LoadMoreNews({
  activeCategory,
  topicId,
  initialCount,
  sortBy = 'relevance'
}: LoadMoreNewsProps) {
  const [additionalArticles, setAdditionalArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  // Number of items to load per page
  const pageSize = 9;

  // Reset state when category, topic, or sort changes (only for main page)
  useEffect(() => {
    setAdditionalArticles([]);
    setHasMore(true);
    setIsLoading(false);
  }, [activeCategory, topicId, sortBy]);

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

      console.log(`Loading more for: ${activeCategory}, topicId: ${topicId}, offset: ${currentOffset}, sortBy: ${sortBy || 'default'}`);

      if (activeCategory === "Vše") {
        // Use sorting only for main page
        moreNews = await fetchLatestNews(pageSize, currentOffset, sortBy);
      } else if (topicId) {
        // For category pages, use the original function without sorting
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
        <div className="grid grid-cols-1 md:grid-cols-1 gap-6 mt-6">
          {additionalArticles.map(article => (
            <ArticleCard article={article} key={article.id} />
          ))}
        </div>
      )}
      
      {/* Load more button or loading indicator */}
      {hasMore && (
        <div className="mt-8 flex justify-center">
          <Button
            onClick={handleLoadMore}
            disabled={isLoading}
            variant="outline"
            size="lg"
            className="min-w-[200px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Načítám články...
              </>
            ) : (
              'Načíst další články'
            )}
          </Button>
        </div>
      )}
    </>
  );
}