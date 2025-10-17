'use client'
import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { fetchLatestNews } from '@/services/api';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';
import PopularNewsSidebar from './PopularNewsSidebar';
import SortDropdown, { SortOption } from '@/components/common/SortDropdown';
import { Card, CardContent, CardHeader } from '~/components/ui/card';
import { Skeleton } from '~/components/ui/skeleton';

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

        {/* Loading state with skeleton */}
        {isLoading ? (
          <div className="space-y-6">
            {/* Featured article skeleton */}
            <Card className="card-elevated overflow-hidden relative">
              <div className="absolute inset-x-0 top-0 h-1.5 ai-gradient shimmer" />
              <CardHeader className="pb-4 pt-8">
                <div className="flex gap-6 items-start flex-col md:flex-row">
                  <Skeleton className="w-24 h-24 rounded-2xl shimmer mx-auto md:mx-0" />
                  <div className="flex-1 space-y-3 text-center md:text-left w-full">
                    <div className="flex items-center gap-2 flex-wrap justify-center md:justify-start">
                      <Skeleton className="h-6 w-20 rounded-full shimmer" />
                      <Skeleton className="h-6 w-32 rounded-full shimmer" />
                    </div>
                    <Skeleton className="h-10 w-full shimmer" />
                    <Skeleton className="h-10 w-3/4 shimmer mx-auto md:mx-0" />
                    <div className="pt-2">
                      <Skeleton className="h-4 w-full shimmer" />
                      <Skeleton className="h-4 w-5/6 shimmer mt-2" />
                    </div>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Article cards skeleton */}
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="card-elevated overflow-hidden">
                <div className="h-1 bg-gradient-to-r from-primary via-primary/60 to-transparent" />
                <CardHeader className="pb-3 pt-4">
                  <div className="flex items-start gap-3">
                    <Skeleton className="w-12 h-12 rounded-xl shimmer" />
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <Skeleton className="h-4 w-20 shimmer" />
                        <Skeleton className="h-4 w-24 shimmer" />
                      </div>
                      <Skeleton className="h-6 w-full shimmer" />
                      <Skeleton className="h-6 w-4/5 shimmer" />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                  <Skeleton className="h-4 w-full shimmer" />
                  <Skeleton className="h-4 w-3/4 shimmer" />
                </CardContent>
              </Card>
            ))}
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