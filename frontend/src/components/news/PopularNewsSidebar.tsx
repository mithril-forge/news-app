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
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center animate-pulse">
              <span className="text-lg">🔥</span>
            </div>
            Nejčtenější články
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex gap-3 items-center">
              <Skeleton className="w-12 h-12 rounded-xl shimmer" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-full shimmer" />
                <Skeleton className="h-3 w-2/3 shimmer" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="card-elevated border-destructive/20">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2 text-destructive">
            <div className="w-8 h-8 rounded-lg bg-destructive/10 flex items-center justify-center">
              <span className="text-lg">⚠️</span>
            </div>
            Chyba načítání
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center py-8 text-muted-foreground text-sm">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="card-elevated relative overflow-hidden">
      {/* Subtle gradient accent */}
      <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-primary via-primary/60 to-transparent" />

      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
            <span className="text-lg">🔥</span>
          </div>
          Nejčtenější články
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-2">
        {popularNews.map((article, index) => {
          const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

          return (
            <Link
              key={article.id}
              href={`/article/${article.id}`}
              className="flex gap-3 items-center p-2.5 rounded-xl hover:bg-accent transition-all group relative"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Number indicator */}
              <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                {index + 1}
              </div>

              {/* Emoji with enhanced styling */}
              <div className="w-12 h-12 rounded-xl bg-accent/50 flex items-center justify-center text-xl flex-shrink-0 border border-border/50 group-hover:scale-110 group-hover:rotate-3 group-hover:bg-accent group-hover:border-primary/20 transition-all duration-300">
                {categoryInfo.emoji}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm leading-tight mb-1.5 group-hover:text-primary transition-colors line-clamp-2">
                  {article.title}
                </h4>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <span>{article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}</span>
                  <span className="w-1 h-1 rounded-full bg-border"></span>
                  <span className="truncate">{article.topic?.name || "Vše"}</span>
                </div>
              </div>
            </Link>
          );
        })}
      </CardContent>
    </Card>
  );
}