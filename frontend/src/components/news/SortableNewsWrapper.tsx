"use client";

import { useState, useEffect } from "react";
import { NewsArticle } from "@/types";
import { fetchLatestNews } from "@/services/api";
import FeaturedArticle from "./FeaturedArticle";
import ArticleCard from "./ArticleCard";
import LoadMoreNews from "./LoadMoreNews";
import PopularNewsSidebar from "./PopularNewsSidebar";
import SortDropdown, { SortOption } from "@/components/common/SortDropdown";

interface SortableNewsWrapperProps {
  initialNews: NewsArticle[];
  activeCategory: string;
  topicId?: string;
}

export default function SortableNewsWrapper({
  initialNews,
  activeCategory,
  topicId,
}: SortableNewsWrapperProps) {
  const [sortBy, setSortBy] = useState<SortOption>("relevance");
  const [news, setNews] = useState<NewsArticle[]>(initialNews);
  const [isLoadingSort, setIsLoadingSort] = useState(false);
  const [isLoadingCategory, setIsLoadingCategory] = useState(false);

  // Reset news when initialNews changes (category change)
  useEffect(() => {
    setIsLoadingCategory(true);

    // Add a small delay to ensure loading state is visible
    const timer = setTimeout(() => {
      setNews(initialNews);
      setSortBy("relevance");
      setIsLoadingCategory(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [initialNews, activeCategory]);

  const handleSortChange = async (newSortBy: SortOption) => {
    if (newSortBy === sortBy) return;

    setIsLoadingSort(true);
    setSortBy(newSortBy);

    try {
      // Add minimum loading time to ensure spinner is visible
      const [sortedNews] = await Promise.all([
        fetchLatestNews(10, 0, newSortBy),
        new Promise(resolve => setTimeout(resolve, 500)) // Minimum 500ms loading
      ]);
      setNews(sortedNews);
    } catch (error) {
      console.error("Error fetching sorted news:", error);
      // Keep original news on error
    } finally {
      setIsLoadingSort(false);
    }
  };

  // Extract featured article and remaining articles
  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);

  // Show loading state for both category and sort changes
  const isLoading = isLoadingSort || isLoadingCategory;

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
      {/* Main content area */}
      <div className="lg:col-span-3">
        {/* Header with sort dropdown */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Všechny články</h2>
          </div>
          <SortDropdown
            currentSort={sortBy}
            onSortChange={handleSortChange}
            disabled={isLoading} // Disable dropdown while loading
          />
        </div>

        {/* Loading state */}
        {isLoading ? (
          <div className="flex items-center justify-center rounded-lg bg-white py-12 shadow">
            <div className="mr-3 h-8 w-8 animate-spin rounded-full border-t-2 border-b-2 border-red-600"></div>
            <span className="text-gray-600">
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