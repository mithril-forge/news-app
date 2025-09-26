// components/news/NewsContent.tsx
import { NewsArticle } from '@/types';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';
import PopularNewsSidebar from './PopularNewsSidebar';
import SortableNewsWrapper from './SortableNewsWrapper';

interface NewsContentProps {
  /** Array of news articles to display */
  news: NewsArticle[];
  /** Currently active category for context */
  activeCategory: string;
  /** Optional topic ID for category-specific news */
  topicId?: string;
}

export default function NewsContent({
  news,
  activeCategory,
  topicId
}: NewsContentProps) {
  // Handle empty state
  if (news.length === 0) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3">
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">
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

  // If this is the main page, wrap with sortable functionality
  if (activeCategory === "Vše") {
    return (
      <SortableNewsWrapper
        initialNews={news}
        activeCategory={activeCategory}
        topicId={topicId}
      />
    );
  }

  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main content area */}
      <div className="lg:col-span-3">
        {/* Category title */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {activeCategory}
          </h2>
        </div>

        {/* Featured article */}
        <FeaturedArticle article={featuredArticle} />
        {/* Article grid */}
        <div className="grid grid-cols-1 gap-6">
          {remainingArticles.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
        {/* Load more articles */}
        <LoadMoreNews
          activeCategory={activeCategory}
          topicId={topicId}
          initialCount={news.length}
        />
      </div>

      {/* Sidebar */}
      <div className="lg:col-span-1">
        <PopularNewsSidebar />
      </div>
    </div>
  );
}