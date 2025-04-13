/**
 * Component for displaying the featured/highlighted article
 * Typically used for the main article at the top of the page
 */
import Image from 'next/image';
import Link from 'next/link';
import { NewsArticle } from '@/types';

interface FeaturedArticleProps {
  /** The featured article to display */
  article: NewsArticle;
}

export default function FeaturedArticle({ article }: FeaturedArticleProps) {
  if (!article) return null; // Safety check

  return (
    <div className="mb-8 bg-white rounded-lg shadow overflow-hidden">
      <div className="md:flex">
        <div className="md:w-1/2">
          <div className="relative w-full h-64 md:h-full">
            {article.image_url && (
              <Image
                src={article.image_url}
                alt={article.title}
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                className="object-cover"
                priority
              />
            )}
          </div>
        </div>
        <div className="md:w-1/2 p-6 flex flex-col">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">{article.title}</h2>
          <p className="text-gray-600 text-lg mb-6">{article.summary}</p>
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm text-gray-500">
              {article.date || new Date(article.updated_at).toLocaleDateString('cs-CZ')}
            </span>
            <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
              {article.topic.name}
            </span>
          </div>
          <div className="flex flex-wrap gap-2 mb-6">
            {(article.tags || []).map(tag => (
              <span key={tag.id} className="text-xs bg-gray-100 px-2 py-1 rounded">
                {tag.text}
              </span>
            ))}
          </div>
          <Link
            href={`/article/${article.id}`}
            className="text-red-600 hover:text-red-800 font-medium flex items-center mt-auto"
          >
            Přečíst celý článek
            <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}