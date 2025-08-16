/**
 * Article detail page component with new emoji design
 * Shows the full content of a single news article
 */
import { Suspense } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

// Import components and API services
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import ArticleContent from '@/components/news/ArticleContent';
import Loading from '@/components/common/Loading';
import InputNewsList from '@/components/news/InputNewsList';
import PopularNewsSidebar from '@/components/news/PopularNewsSidebar';
import { fetchNewsById, fetchTopics } from '@/services/api';
import { NewsDetailed } from '@/types';
import { getCategoryEmoji } from '@/lib/categoryEmoji';

interface ArticlePageProps {
  params: Promise<{
    id: string;
  }>;
}

/**
 * Generate dynamic metadata for SEO
 */
export async function generateMetadata({ 
  params 
}: ArticlePageProps): Promise<Metadata> {
  const { id } = await params;
  const article = await fetchNewsById(id);
  
  if (!article) {
    return {
      title: 'Článek nenalezen | Tvůj Novinář',
      description: 'Požadovaný článek nebyl nalezen.',
    };
  }
  
  return {
    title: `${article.title} | Tvůj Novinář`,
    description: article.summary || 'Přečtěte si nejnovější zprávy na Tvůj Novinář',
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
  // Await params first
  const { id } = await params;
  
  // Parallel data fetching for efficiency
  const [article, topicsData] = await Promise.all([
    fetchNewsById(id),
    fetchTopics()
  ]);
  
  // Handle 404 if article not found
  if (!article) {
    notFound();
  }
  
  // Ensure article is treated as NewsDetailed type
  const fullArticle = article as NewsDetailed;
  
  // Prepare categories for header/footer
  const categories = ["AI Feed", "Vše", ...topicsData.map(topic => topic.name)];
  const activeCategory = fullArticle.topic?.name || "Vše";
  
  // Get category emoji info
  const categoryInfo = getCategoryEmoji(fullArticle.topic?.name || 'Vše');

  return (
    <div className="min-h-screen flex flex-col" style={{
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
      />
      
      <Suspense fallback={<Loading />}>
        <main className="max-w-7xl mx-auto px-4 py-8 w-full flex-grow">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main article content */}
            <div className="lg:col-span-3">
              <article className="bg-white rounded-3xl shadow-xl overflow-hidden">
                {/* Gradient top border */}
                <div className="h-1 bg-gradient-to-r from-red-500 via-orange-500 to-blue-500"></div>
                
                {/* Article header */}
                <div className="p-8">
                  {/* Category emoji and meta info */}
                  <div className="flex items-center gap-6 mb-6">
                    <div 
                      className="w-20 h-20 rounded-2xl flex items-center justify-center text-3xl border-3 shadow-lg"
                      style={{ 
                        borderColor: categoryInfo.color,
                        background: categoryInfo.bgColor
                      }}
                    >
                      {categoryInfo.emoji}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex flex-wrap gap-3 mb-2">
                        <span 
                          className="px-4 py-2 rounded-full text-sm font-medium"
                          style={{ 
                            backgroundColor: `${categoryInfo.color}20`, 
                            color: categoryInfo.color 
                          }}
                        >
                          {fullArticle.topic?.name || "Vše"}
                        </span>
                        <span className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full text-sm">
                          {new Date(fullArticle.updated_at).toLocaleDateString('cs-CZ')}
                        </span>
                      </div>
                      
                      {/* Tags */}
                      {fullArticle.tags && fullArticle.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {fullArticle.tags.slice(0, 4).map(tag => (
                            <span key={tag.id} className="text-xs bg-gray-100 px-3 py-1 rounded-full text-gray-600">
                              {tag.text}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Article title */}
                  <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-8 leading-tight">
                    {fullArticle.title}
                  </h1>

                  {/* Article summary */}
                  {fullArticle.summary && (
                    <div className="mb-8 p-6 bg-gray-50 rounded-2xl border-l-4" style={{ borderLeftColor: categoryInfo.color }}>
                      <p className="text-lg text-gray-700 leading-relaxed font-medium">
                        {fullArticle.summary}
                      </p>
                    </div>
                  )}

                  {/* Article content */}
                  <div className="prose prose-lg max-w-none text-gray-700">
                    <ArticleContent content={fullArticle.content} />
                  </div>
                </div>

                {/* Input News Section */}
                {fullArticle.input_news && fullArticle.input_news.length > 0 && (
                  <div className="p-8 bg-gray-50 border-t">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-xl">
                        🔗
                      </div>
                      <h2 className="text-2xl font-bold text-gray-800">
                        Zdroje článku
                      </h2>
                    </div>
                    <InputNewsList inputNews={fullArticle.input_news} />
                  </div>
                )}

                {/* Navigation */}
                <div className="p-8 bg-gray-50 border-t">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <Link 
                      href="/" 
                      className="text-red-600 hover:text-red-800 font-medium inline-flex items-center gap-2 transition-all hover:gap-4"
                    >
                      ← Zpět na přehled zpráv
                    </Link>
                    
                    <Link 
                      href={`/?category=${encodeURIComponent(fullArticle.topic?.name || "Vše")}`}
                      className="text-red-600 hover:text-red-800 font-medium inline-flex items-center gap-2 transition-all hover:gap-4"
                    >
                      Zobrazit více z kategorie {fullArticle.topic?.name || "Vše"} →
                    </Link>
                  </div>
                </div>
              </article>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <PopularNewsSidebar />
          
            </div>
          </div>
        </main>
      </Suspense>
      
      <Footer 
        categories={categories} 
      />
    </div>
  );
}