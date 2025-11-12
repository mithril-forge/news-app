// app/page.tsx
import { Suspense } from 'react';
import { fetchTopics, fetchLatestNews, fetchNewsByTopic, searchNews } from '@/services/api';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import NewsContent from '@/components/news/NewsContent';
import Loading from '@/components/common/Loading';

// Configure ISR (Incremental Static Regeneration)
export const revalidate = 600; // Revalidate this page every 10 minutes

interface HomePageProps {
  searchParams: Promise<{
    category?: string;
    q: string;
  }>;
}

export default async function HomePage({ searchParams }: HomePageProps) {
  // Get the category from URL query params with a default of "Vše"
  const resolvedSearchParams = await searchParams;
  const search = resolvedSearchParams.q;
  const activeCategory = resolvedSearchParams.category || "Vše";

  // Fetch data on the server
  const topicsData = await fetchTopics();
  const categories = ["AI Feed", "Vše", ...topicsData.map(topic => topic.name)];

  // Fetch the appropriate news data based on selected category
  let newsData;
  newsData = await searchNews(search);
  if (newsData === null) {
    newsData = []
  }
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
          <NewsContent
            news={newsData}
            activeCategory={activeCategory}
            enableSorting={false}
            loadMoreNews={false}
          />
        </main>
      </Suspense>

      <Footer
        categories={categories}
      />
    </div>
  );
}
