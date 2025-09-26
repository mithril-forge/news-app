// components/news/ArticleCard.tsx
import Link from 'next/link';
import { NewsArticle } from '@/types';
import { getCategoryEmoji } from '@/lib/categoryEmoji';

interface ArticleCardProps {
  article: NewsArticle;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  // Safety check for undefined article
  if (!article) {
    return null;
  }

  const categoryInfo = getCategoryEmoji(article.topic?.name || 'Vše');

  // Function to get first 100-150 characters from description
  const getDescriptionPreview = (description?: string) => {
    if (!description) return '';

    const trimmed = description.trim();
    const maxLength = 120; // Adjust this number as needed

    if (trimmed.length <= maxLength) {
      return trimmed;
    }

    // Truncate at character limit but try to end at a word boundary
    let preview = trimmed.slice(0, maxLength);
    const lastSpaceIndex = preview.lastIndexOf(' ');

    // If we found a space near the end, cut there for cleaner text
    if (lastSpaceIndex > maxLength - 20) {
      preview = preview.slice(0, lastSpaceIndex);
    }

    return `${preview}...`;
  };

  return (
    <Link href={`/article/${article.id}`} className="block group">
      <article className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex gap-6 flex-col sm:flex-row cursor-pointer">
        {/* Emoji icon */}
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 border-3 group-hover:scale-110 transition-transform duration-300 mx-auto sm:mx-0"
          style={{
            borderColor: categoryInfo.color,
            borderWidth: '3px',
            borderStyle: 'solid',
            background: categoryInfo.bgColor
          }}
        >
          {categoryInfo.emoji}
        </div>

        {/* Content */}
        <div className="flex-1 text-center sm:text-left">
          <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
            <span className="text-gray-500 text-sm">
              {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
            </span>
            <span
              className="px-3 py-1 rounded-full text-xs font-medium"
              style={{
                backgroundColor: `${categoryInfo.color}20`,
                color: categoryInfo.color
              }}
            >
              {article.topic?.name || "Vše"}
            </span>
          </div>

          <h2 className="text-xl font-semibold text-gray-800 mb-3 leading-tight group-hover:text-red-600 transition-colors">
            {article.title}
          </h2>

          {/* Description Preview */}
          {article.description && (
            <p className="text-gray-600 text-sm mb-3 leading-relaxed">
              {getDescriptionPreview(article.description)}
            </p>
          )}

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3 justify-center sm:justify-start">
              {article.tags.slice(0, 2).map(tag => (
                <span key={tag} className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}

          <span className="text-red-600 group-hover:text-red-800 font-medium inline-flex items-center gap-2 transition-all group-hover:gap-4">
            Přečíst článek →
          </span>
        </div>
      </article>
    </Link>
  );
}
