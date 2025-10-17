// components/news/PopularNewsSidebar.tsx
'use client'

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { NewsArticle } from '@/types';
import { fetchPopularNews } from '@/services/api';
import { getCategoryEmoji } from '@/lib/categoryEmoji';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Skeleton } from '~/components/ui/skeleton';

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
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Nejčtenější články za poslední týden</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex gap-3 items-center">
              <Skeleton className="w-11 h-11 rounded-lg" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Nejčtenější články za poslední týden</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center py-8 text-muted-foreground">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Nejčtenější články za poslední týden</CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {popularNews.map((article) => {
          const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

          return (
            <Link
              key={article.id}
              href={`/article/${article.id}`}
              className="flex gap-3 items-center p-2 rounded-lg hover:bg-accent transition-all group"
            >
              {/* Emoji */}
              <div className="w-11 h-11 rounded-lg bg-secondary flex items-center justify-center text-lg flex-shrink-0 border border-border group-hover:scale-105 transition-transform">
                {categoryInfo.emoji}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm leading-tight mb-1 group-hover:text-primary transition-colors line-clamp-2">
                  {article.title}
                </h4>
                <div className="text-xs text-muted-foreground">
                  {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')} • {article.topic?.name || "Vše"}
                </div>
              </div>
            </Link>
          );
        })}
      </CardContent>
    </Card>
  );
}