import Link from 'next/link';
import { NewsArticle } from '@/types';
import { getCategoryEmoji } from '@/lib/categoryEmoji';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { ArrowRight } from 'lucide-react';

interface ArticleCardProps {
  article: NewsArticle;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  if (!article) {
    return null;
  }

  const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

  const getDescriptionPreview = (description?: string) => {
    if (!description) return '';

    const trimmed = description.trim();
    const maxLength = 150;

    if (trimmed.length <= maxLength) {
      return trimmed;
    }

    let preview = trimmed.slice(0, maxLength);
    const lastSpaceIndex = preview.lastIndexOf(' ');

    if (lastSpaceIndex > maxLength - 20) {
      preview = preview.slice(0, lastSpaceIndex);
    }

    return `${preview}...`;
  };

  return (
    <Link href={`/article/${article.id}`} className="block group">
      <Card className="card-elevated overflow-hidden border-border/50 hover:border-primary/30">
        {/* Top accent line with gradient */}
        <div className="h-1 bg-gradient-to-r from-primary via-primary/60 to-transparent" />

        <CardHeader className="pb-3 pt-4">
          <div className="flex items-start gap-3">
            {/* Category icon */}
            <div className="w-12 h-12 rounded-xl bg-accent/50 flex items-center justify-center text-xl flex-shrink-0 border border-border/50 transition-all duration-200 group-hover:scale-110 group-hover:bg-accent group-hover:border-primary/20">
              {categoryInfo.emoji}
            </div>

            <div className="flex-1 min-w-0 space-y-2">
              {/* Date and category */}
              <div className="flex items-center gap-2 flex-wrap">
                <time className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
                </time>
                <span className="w-1 h-1 rounded-full bg-border"></span>
                <Badge variant="secondary" className="text-xs font-medium">
                  {article.topic?.name || "Vše"}
                </Badge>
              </div>

              <CardTitle className="text-lg leading-snug group-hover:text-primary transition-colors line-clamp-2">
                {article.title}
              </CardTitle>
            </div>
          </div>
        </CardHeader>

        {(article.description || (article.tags && article.tags.length > 0)) && (
          <CardContent className="pt-0 space-y-3">
            {/* Description */}
            {article.description && (
              <CardDescription className="text-sm leading-relaxed line-clamp-2">
                {getDescriptionPreview(article.description)}
              </CardDescription>
            )}

            {/* Tags and read more */}
            <div className="flex items-center justify-between gap-3 flex-wrap pt-1">
              {article.tags && article.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {article.tags.slice(0, 2).map(tag => (
                    <Badge key={tag} variant="outline" className="text-xs font-normal">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}

              <span className="text-sm font-medium text-primary inline-flex items-center gap-1.5 group-hover:gap-2 transition-all ml-auto">
                Číst článek
                <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </CardContent>
        )}
      </Card>
    </Link>
  );
}
