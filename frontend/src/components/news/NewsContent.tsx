/**
 * Server component for displaying all news content
 * With proper grid layout for article cards
 */
import { NewsArticle } from '@/types';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';
import LoadMoreNews from './LoadMoreNews';

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
      <div className="md:col-span-3 text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500">
          Žádné články nebyly nalezeny v kategorii '{activeCategory}'
        </p>
      </div>
    );
  }

  // Extract featured article and remaining articles
  const featuredArticle = news[0];
  const remainingArticles = news.slice(1);

  return (
    <>
      {/* Featured article - rendered on server */}
      <FeaturedArticle article={featuredArticle} />
      
      {/* Article grid with proper responsive layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {remainingArticles.map(item => (
          <ArticleCard key={item.id} item={item} />
        ))}
      </div>
      
      {/* Client component for loading more articles */}
      <LoadMoreNews
        activeCategory={activeCategory}
        topicId={topicId}
        initialCount={news.length}
      />
    </>
  );
}