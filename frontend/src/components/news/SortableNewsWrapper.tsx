'use client';

import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { fetchLatestNews } from '@/services/api';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';
import PopularNewsSidebar from './PopularNewsSidebar';
import SortDropdown, { SortOption } from '@/components/common/SortDropdown';

interface SortableNewsWrapperProps {
  initialNews: NewsArticle[];
  activeCategory: string;
  topicId?: string;
}

export default function SortableNewsWrapper({
  initialNews,
  activeCategory,
  topicId
}: SortableNewsWrapperProps) {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [news, setNews] = useState<NewsArticle[]>(initialNews);
  const [isLoadingSort, setIsLoadingSort] = useState(false);

  // Reset news when initialNews changes (category change)
  useEffect(() => {
    setNews(initialNews);
    setSortBy('relevance');
  }, [initialNews]);

  const handleSortChange = async (newSortBy: SortOption) => {
    if (newSortBy === sortBy) return;

    setIsLoadingSort(true);
    setSortBy(newSortBy);

    try {
      const sortedNews = await fetchLatestNews(10, 0, newSortBy);
      setNews(sortedNews);
    } catch (error) {
      console.error('Error fetching sorted news:', error);
      // Keep original news on error
    } finally {
      setIsLoadingSort(false);
    }
  };

  // Extract featured article and remaining articles
  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main content area */}
      <div className="lg:col-span-3">
        {/* Header with sort dropdown */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Všechny články
            </h2>
          </div>
          <SortDropdown currentSort={sortBy} onSortChange={handleSortChange} />
        </div>

        {/* Loading state for sorting */}
        {isLoadingSort ? (
          <div className="flex justify-center items-center py-12 bg-white rounded-lg shadow">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-600 mr-3"></div>
            <span className="text-gray-600">Načítám články...</span>
          </div>
        ) : (
          <>
            {/* Featured article */}
            {featuredArticle && (
              <FeaturedArticle article={featuredArticle} />
            )}

            {/* Article grid */}
            {remainingArticles.length > 0 && (
              <div className="grid grid-cols-1 gap-6">
                {remainingArticles.map(item => (
                  <ArticleCard key={item.id} item={item} />
                ))}
              </div>
            )}

            {/* Load more articles */}
            <LoadMoreNews
              activeCategory={activeCategory}
              topicId={topicId}
              initialCount={news.length}
              sortBy={sortBy}
            />
          </>
        )}
      </div>

      {/* Sidebar */}
      <div className="lg:col-span-1">
        <PopularNewsSidebar />
      </div>
    </div>
  );
}