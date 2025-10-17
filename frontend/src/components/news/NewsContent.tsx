'use client'
import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { fetchLatestNews } from '@/services/api';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';
import PopularNewsSidebar from './PopularNewsSidebar';
import SortDropdown, { SortOption } from '@/components/common/SortDropdown';

interface NewsContentProps {
  news: NewsArticle[];
  activeCategory: string;
  topicId?: string;
  enableSorting?: boolean; // New prop to control sorting
}

export default function NewsContent({
  news: initialNews,
  activeCategory,
  topicId,
  enableSorting = false // Default to false, only enable for main page
}: NewsContentProps) {
  const [sortBy, setSortBy] = useState<SortOption>("relevance");
  const [news, setNews] = useState<NewsArticle[]>(initialNews);
  const [isLoadingSort, setIsLoadingSort] = useState(false);
  const [isLoadingCategory, setIsLoadingCategory] = useState(false);

  // Reset news when initialNews changes (category change)
  useEffect(() => {
    setIsLoadingCategory(true);

    const timer = setTimeout(() => {
      setNews(initialNews);
      setSortBy("relevance");
      setIsLoadingCategory(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [initialNews, activeCategory]);

  const handleSortChange = async (newSortBy: SortOption) => {
    if (newSortBy === sortBy || !enableSorting) return;

    setIsLoadingSort(true);
    setSortBy(newSortBy);

    try {
      const [sortedNews] = await Promise.all([
        fetchLatestNews(10, 0, newSortBy),
        new Promise(resolve => setTimeout(resolve, 150))
      ]);
      setNews(sortedNews);
    } catch (error) {
      console.error("Error fetching sorted news:", error);
    } finally {
      setIsLoadingSort(false);
    }
  };

  // Handle empty state
  if (initialNews.length === 0) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3">
          <div className="text-center py-12 bg-card rounded-lg border">
            <p className="text-muted-foreground">
              Žádné články nebyly nalezeny v kategorii '{activeCategory}'
            </p>
          </div>
        </div>
        <div className="lg:col-span-1">
          <PopularNewsSidebar />
        </div>
      </div>
    );
  }

  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);
  const isLoading = isLoadingSort || isLoadingCategory;

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
      <div className="lg:col-span-3">
        {/* Header with optional sort dropdown */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">
              {activeCategory === "Vše" ? "Všechny články" : activeCategory}
            </h2>
          </div>
          {enableSorting && (
            <SortDropdown
              currentSort={sortBy}
              onSortChange={handleSortChange}
              disabled={isLoading}
            />
          )}
        </div>

        {/* Loading state */}
        {isLoading ? (
          <div className="flex items-center justify-center rounded-lg bg-card border py-12">
            <div className="mr-3 h-8 w-8 animate-spin rounded-full border-t-2 border-b-2 border-primary"></div>
            <span className="text-muted-foreground">
              {isLoadingCategory ? "Načítám kategorii..." : "Načítám články..."}
            </span>
          </div>
        ) : (
          <>
            {/* Featured article */}
            {featuredArticle && <FeaturedArticle article={featuredArticle} />}
            
            {/* Article grid */}
            {remainingArticles.length > 0 && (
              <div className="grid grid-cols-1 gap-6">
                {remainingArticles.map((item) => (
                  <ArticleCard article={item} key={item.id} />
                ))}
              </div>
            )}

            {/* Load more articles */}
            <LoadMoreNews
              activeCategory={activeCategory}
              topicId={topicId}
              initialCount={news.length}
              sortBy={enableSorting ? sortBy : undefined}
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