// components/news/PopularNewsSidebar.tsx
'use client'

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { NewsArticle } from '@/types';
import { fetchPopularNews } from '@/services/api';
import { getCategoryEmoji } from '@/lib/categoryEmoji';

export default function PopularNewsSidebar() {
  const [popularNews, setPopularNews] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPopularNews = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchPopularNews(7, 5); // Načteme 5 nejpopulárnějších
        setPopularNews(data);
      } catch (error) {
        console.error('Error loading popular news:', error);
        setError('Nepodařilo se načíst populární články');
      } finally {
        setIsLoading(false);
      }
    };

    loadPopularNews();
  }, []);

  if (isLoading) {
    return (
      <aside className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-semibold text-gray-800 mb-6 pb-2 border-b-2 border-gray-100">
          Nejčtenější články za poslední týden
        </h3>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="flex gap-4 items-center">
                <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>
    );
  }

  if (error) {
    return (
      <aside className="bg-white rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-semibold text-gray-800 mb-6 pb-2 border-b-2 border-gray-100">
          Nejčtenější články za poslední týden
        </h3>
        <div className="text-center py-8 text-gray-500">
          <p>{error}</p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="bg-white rounded-2xl p-6 shadow-lg">
      <h3 className="text-xl font-semibold text-gray-800 mb-6 pb-2 border-b-2 border-gray-100">
        Nejčtenější články za poslední týden
      </h3>
      
      <div className="space-y-4">
        {popularNews.map((article, index) => {
          const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');
          
          return (
            <Link
              key={article.id}
              href={`/article/${article.id}`}
              className="flex gap-4 items-center p-3 rounded-xl hover:bg-gray-50 transition-all duration-300 hover:scale-105 cursor-pointer group"
            >
              {/* Emoji */}
              <div 
                className="w-12 h-12 rounded-xl flex items-center justify-center text-xl flex-shrink-0 border-2 group-hover:scale-110 transition-transform"
                style={{ 
                  borderColor: categoryInfo.color,
                  background: categoryInfo.bgColor
                }}
              >
                {categoryInfo.emoji}
              </div>
              
              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-800 text-sm leading-tight mb-1 group-hover:text-red-600 transition-colors line-clamp-2">
                  {article.title}
                </h4>
                <div className="text-xs text-gray-500">
                  {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')} • {article.topic?.name || "Vše"}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}