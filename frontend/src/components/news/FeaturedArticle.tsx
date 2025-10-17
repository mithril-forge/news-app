import Link from 'next/link';
import { NewsArticle } from '@/types';
import { getCategoryEmoji } from '@/lib/categoryEmoji';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { ArrowRight } from 'lucide-react';

interface FeaturedArticleProps {
  article: NewsArticle;
}

export default function FeaturedArticle({ article }: FeaturedArticleProps) {
  if (!article) return null;

  const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

  const getDescriptionPreview = (description?: string) => {
    if (!description) return '';

    const words = description.trim().split(/\s+/);
    const previewWords = words.slice(0, 25);
    const preview = previewWords.join(' ');

    return words.length > 25 ? `${preview}...` : preview;
  };

  return (
    <Link href={`/article/${article.id}`} className="block group mb-8">
      <Card className="card-elevated overflow-hidden border-2 border-primary/20 hover:border-primary/40 bg-gradient-to-br from-card to-accent/20">
        <div className="absolute inset-x-0 top-0 h-1.5 ai-gradient" />

        <CardHeader className="pb-4 pt-8">
          <div className="flex gap-6 items-start flex-col md:flex-row">
            {/* Category icon */}
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border-2 border-primary/30 flex items-center justify-center text-5xl flex-shrink-0 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 mx-auto md:mx-0 shadow-lg shadow-primary/10">
              {categoryInfo.emoji}
            </div>

            <div className="flex-1 space-y-3 text-center md:text-left">
              {/* Date and category */}
              <div className="flex items-center gap-2 flex-wrap justify-center md:justify-start">
                <time className="text-sm text-muted-foreground uppercase tracking-wide font-medium">
                  {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
                </time>
                <span className="text-muted-foreground/50">•</span>
                <Badge variant="default" className="font-medium">
                  {article.topic?.name || "Vše"}
                </Badge>
                {article.tags?.slice(0, 2).map(tag => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              <CardTitle className="text-3xl md:text-4xl leading-tight group-hover:text-primary transition-colors">
                {article.title}
              </CardTitle>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {article.description && (
            <CardDescription className="text-base leading-relaxed">
              {getDescriptionPreview(article.description)}
            </CardDescription>
          )}

          <div className="pt-2">
            <span className="text-base font-semibold text-primary inline-flex items-center gap-2 group-hover:gap-3 transition-all">
              Přečíst celý článek
              <ArrowRight className="h-4 w-4" />
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}