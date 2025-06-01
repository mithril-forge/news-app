// components/news/NewsContent.tsx
import { NewsArticle } from '@/types';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';
import PopularNewsSidebar from './PopularNewsSidebar';

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

  // Extract featured article and remaining articles
  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main content area */}
      <div className="lg:col-span-3">
        {/* Featured article */}
        <FeaturedArticle article={featuredArticle} />
        
        {/* Article grid */}
        <div className="grid grid-cols-1 gap-6">
          {remainingArticles.map(item => (
            <ArticleCard key={item.id} item={item} />
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