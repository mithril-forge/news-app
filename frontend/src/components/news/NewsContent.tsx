/**
 * Container component for displaying all news content
 * Handles the featured article and grid of remaining articles
 */
import { NewsArticle } from '@/types';
import FeaturedArticle from './FeaturedArticle';
import ArticleCard from './ArticleCard';

interface NewsContentProps {
  /** Array of news articles to display */
  news: NewsArticle[];
  /** Currently active category for context */
  activeCategory: string;
}

export default function NewsContent({ news, activeCategory }: NewsContentProps) {
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
      <FeaturedArticle article={featuredArticle} />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {remainingArticles.length > 0 ? (
          remainingArticles.map(item => (
            <ArticleCard key={item.id} item={item} />
          ))
        ) : (
          activeCategory !== "Vše" && (
            <div className="md:col-span-3 text-center py-12">
              <p className="text-gray-500">
                Žádné další články v kategorii '{activeCategory}'
              </p>
            </div>
          )
        )}
      </div>
    </>
  );
}