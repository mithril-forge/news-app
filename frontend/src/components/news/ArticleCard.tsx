/**
 * Card component for displaying a news article in a list/grid
 */
import Image from 'next/image';
import Link from 'next/link';
import { NewsArticle } from '@/types';

interface ArticleCardProps {
  /** The news article to display */
  item: NewsArticle;
}

export default function ArticleCard({ item }: ArticleCardProps) {
  return (
    <article className="bg-white rounded-lg shadow overflow-hidden flex flex-col">
      <div className="relative w-full h-48">
        {item.image_url && (
          <Image
            src={item.image_url}
            alt={item.title}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            className="object-cover"
          />
        )}
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h2 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h2>
        <p className="text-gray-600 mb-3 line-clamp-3 flex-grow">{item.summary}</p>
        <div className="flex justify-between items-center mt-2">
          <span className="text-sm text-gray-500">
            {item.date || new Date(item.updated_at).toLocaleDateString('cs-CZ')}
          </span>
          <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {item.topic.name}
          </span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {(item.tags || []).slice(0, 3).map(tag => (
            <span key={tag.id} className="text-xs bg-gray-100 px-2 py-1 rounded">
              {tag.text}
            </span>
          ))}
        </div>
        <Link
          href={`/article/${item.id}`}
          className="mt-4 text-red-600 hover:text-red-800 text-sm font-medium block"
        >
          Přečíst článek →
        </Link>
      </div>
    </article>
  );
}