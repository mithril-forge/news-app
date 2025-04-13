/**
 * Article detail page component
 * Shows the full content of a single news article
 */
import { Suspense } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

// Import components and API services
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import ArticleContent from '@/components/news/ArticleContent';
import Loading from '@/components/common/Loading';
import { fetchNewsById, fetchTopics } from '@/services/api';

interface ArticlePageProps {
  params: {
    id: string;
  };
}

/**
 * Generate dynamic metadata for SEO
 */
export async function generateMetadata({ 
  params 
}: ArticlePageProps): Promise<Metadata> {
  const article = await fetchNewsById(params.id);
  
  if (!article) {
    return {
      title: 'Článek nenalezen | ZPRÁVY.CZ',
      description: 'Požadovaný článek nebyl nalezen.',
    };
  }
  
  return {
    title: `${article.title} | ZPRÁVY.CZ`,
    description: article.summary || 'Přečtěte si nejnovější zprávy na ZPRÁVY.CZ',
    openGraph: {
      title: article.title,
      description: article.summary,
      images: article.image_url ? [{ url: article.image_url }] : [],
    },
  };
}

// Configure ISR revalidation
export const revalidate = 3600; // Revalidate every hour

export default async function ArticlePage({ params }: ArticlePageProps) {
  // Parallel data fetching for efficiency
  const [article, topicsData] = await Promise.all([
    fetchNewsById(params.id),
    fetchTopics()
  ]);
  
  // Handle 404 if article not found
  if (!article) {
    notFound();
  }
  
  // Prepare categories for header/footer
  const categories = ["Vše", ...topicsData.map(topic => topic.name)];
  const activeCategory = article.topic.name;
  
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
      />
      
      <Suspense fallback={<Loading />}>
        <main className="max-w-3xl mx-auto px-4 py-8 w-full flex-grow">
          <article>
            {/* Category and date */}
            <div className="mb-4 text-sm text-gray-600">
              <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">
                {article.topic.name}
              </span>
              <span>{new Date(article.updated_at).toLocaleDateString('cs-CZ')}</span>
            </div>

            {/* Article title */}
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
              {article.title}
            </h1>

            {/* Featured image */}
            <div className="mb-8 relative w-full aspect-video bg-gray-200 rounded overflow-hidden">
              {article.image_url && (
                <Image
                  src={article.image_url}
                  alt={article.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 768px"
                  className="object-cover"
                  priority
                />
              )}
            </div>

            {/* Article content */}
            <ArticleContent content={article.content} />
            
            {/* Tags section */}
            {article.tags && article.tags.length > 0 && (
              <div className="mt-8 pt-4 border-t border-gray-200">
                <span className="text-gray-500 text-sm mr-2">Štítky:</span>
                {article.tags.map(tag => (
                  <span key={tag.id} className="inline-block text-xs bg-gray-100 px-2 py-1 rounded mr-2 mb-2">
                    {tag.text}
                  </span>
                ))}
              </div>
            )}

            {/* Back to home link */}
            <div className="mt-8">
              <Link href="/" className="text-red-600 hover:text-red-800">
                &larr; Zpět na přehled zpráv
              </Link>
            </div>
          </article>
        </main>
      </Suspense>
      
      <Footer 
        categories={categories} 
      />
    </div>
  );
}