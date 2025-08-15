// components/news/FeaturedArticle.tsx
import Link from 'next/link';
import { NewsArticle } from '@/types';
import { getCategoryEmoji } from '@/lib/categoryEmoji';

interface FeaturedArticleProps {
  article: NewsArticle;
}

export default function FeaturedArticle({ article }: FeaturedArticleProps) {
  if (!article) return null;

  const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

  // Function to get first 20-25 words from description (more for featured article)
  const getDescriptionPreview = (description?: string) => {
    if (!description) return '';
    
    const words = description.trim().split(/\s+/);
    const previewWords = words.slice(0, 20); // Take first 20 words for featured article
    const preview = previewWords.join(' ');
    
    // Add ellipsis if description was truncated
    return words.length > 20 ? `${preview}...` : preview;
  };

  return (
    <Link href={`/article/${article.id}`} className="block group">
      <article className="bg-white rounded-3xl p-8 mb-8 shadow-xl relative overflow-hidden cursor-pointer hover:shadow-2xl transition-all duration-300">
        {/* Gradient top border */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-blue-500"></div>
        
        <div className="flex gap-6 items-center flex-col md:flex-row text-center md:text-left">
          {/* Hero emoji */}
          <div 
            className="w-32 h-32 rounded-3xl flex items-center justify-center text-6xl flex-shrink-0 border-4 shadow-2xl group-hover:scale-105 transition-transform duration-300"
            style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderColor: 'rgba(255,255,255,0.2)'
            }}
          >
            {categoryInfo.emoji}
          </div>
          
          {/* Content */}
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-gray-800 mb-4 leading-tight group-hover:text-red-600 transition-colors">
              {article.title}
            </h1>

            {/* Description Preview */}
            {article.description && (
              <p className="text-gray-600 text-lg mb-6 leading-relaxed">
                {getDescriptionPreview(article.description)}
              </p>
            )}

            <div className="flex gap-4 mb-6 flex-wrap justify-center md:justify-start">
              <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-medium">
                {article.topic?.name || "Vše"}
              </span>
              <span className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full text-sm">
                {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
              </span>
              {article.tags?.slice(0, 2).map(tag => (
                <span key={tag} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
            <span className="text-red-600 group-hover:text-red-800 font-medium text-lg inline-flex items-center gap-2 transition-all group-hover:gap-4">
              Přečíst celý článek →
            </span>
          </div>
        </div>
      </article>
    </Link>
  );
}