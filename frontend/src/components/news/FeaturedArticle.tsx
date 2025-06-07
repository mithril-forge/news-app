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

  return (
    <article className="bg-white rounded-3xl p-8 mb-8 shadow-xl relative overflow-hidden">
      {/* Gradient top border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-blue-500"></div>
      
      <div className="flex gap-6 items-center flex-col md:flex-row text-center md:text-left">
        {/* Hero emoji */}
        <div 
          className="w-32 h-32 rounded-3xl flex items-center justify-center text-6xl flex-shrink-0 border-4 shadow-2xl hover:scale-105 transition-transform duration-300 cursor-pointer"
          style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderColor: 'rgba(255,255,255,0.2)'
          }}
        >
          {categoryInfo.emoji}
        </div>
        
        {/* Content */}
        <div className="flex-1">
          <h1 className="text-4xl font-bold text-gray-800 mb-4 leading-tight">
            {article.title}
          </h1>
          <div className="flex gap-4 mb-6 flex-wrap justify-center md:justify-start">
            <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-medium">
              {article.topic?.name || "Vše"}
            </span>
            <span className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full text-sm">
              {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
            </span>
            {article.tags?.slice(0, 2).map(tag => (
              <span key={tag.id} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full text-sm">
                {tag.text}
              </span>
            ))}
          </div>
          <Link
            href={`/article/${article.id}`}
            className="text-red-600 hover:text-red-800 font-medium text-lg inline-flex items-center gap-2 transition-all hover:gap-4"
          >
            Přečíst celý článek →
          </Link>
        </div>
      </div>
    </article>
  );
}