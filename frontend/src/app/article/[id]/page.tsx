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
import { Card, CardContent, CardHeader } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import { Separator } from '~/components/ui/separator';
import { ArrowLeft, ArrowRight, Link2 } from 'lucide-react';

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
    <div className="min-h-screen flex flex-col bg-background">
      <Header
        categories={categories}
        activeCategory={activeCategory}
      />

      <Suspense fallback={<Loading />}>
        <main className="max-w-7xl mx-auto px-4 py-8 w-full flex-grow">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main article content */}
            <div className="lg:col-span-3">
              <Card className="overflow-hidden">
                {/* Top accent line */}
                <div className="h-1 bg-primary" />

                {/* Article header */}
                <CardHeader className="pb-6">
                  {/* Category emoji and meta info */}
                  <div className="flex items-center gap-6 mb-6">
                    <div className="w-20 h-20 rounded-xl bg-secondary flex items-center justify-center text-3xl border border-border">
                      {categoryInfo.emoji}
                    </div>

                    <div className="flex-1">
                      <div className="flex flex-wrap gap-2 mb-3">
                        <Badge variant="default" className="text-sm">
                          {fullArticle.topic?.name || "Vše"}
                        </Badge>
                        <Badge variant="secondary" className="text-sm">
                          {new Date(fullArticle.updated_at).toLocaleDateString('cs-CZ')}
                        </Badge>
                      </div>

                      {/* Tags */}
                      {fullArticle.tags && fullArticle.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {fullArticle.tags.slice(0, 4).map(tag => (
                            <Badge key={tag.id} variant="outline" className="text-xs">
                              {tag.text}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Article title */}
                  <h1 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
                    {fullArticle.title}
                  </h1>

                  {/* Article summary */}
                  {fullArticle.summary && (
                    <div className="p-6 bg-muted/50 rounded-lg border-l-4 border-primary">
                      <p className="text-lg leading-relaxed font-medium">
                        {fullArticle.summary}
                      </p>
                    </div>
                  )}
                </CardHeader>

                <CardContent className="pt-0">
                  {/* Article content */}
                  <div className="prose prose-lg max-w-none">
                    <ArticleContent content={fullArticle.content} />
                  </div>
                </CardContent>

                {/* Input News Section */}
                {fullArticle.input_news && fullArticle.input_news.length > 0 && (
                  <>
                    <Separator />
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
                          <Link2 className="h-5 w-5 text-primary" />
                        </div>
                        <h2 className="text-2xl font-bold">
                          Zdroje článku
                        </h2>
                      </div>
                      <InputNewsList inputNews={fullArticle.input_news} />
                    </CardContent>
                  </>
                )}

                {/* Navigation */}
                <Separator />
                <CardContent className="pt-6">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <Button variant="ghost" asChild className="gap-2">
                      <Link href="/">
                        <ArrowLeft className="h-4 w-4" />
                        Zpět na přehled zpráv
                      </Link>
                    </Button>

                    <Button variant="ghost" asChild className="gap-2">
                      <Link href={`/?category=${encodeURIComponent(fullArticle.topic?.name || "Vše")}`}>
                        Zobrazit více z kategorie {fullArticle.topic?.name || "Vše"}
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
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