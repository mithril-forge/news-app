/**
 * Home page component showing the latest news and filterable by category
 * Server component that handles data fetching
 */
import { Suspense } from 'react';
import { fetchTopics, fetchLatestNews, fetchNewsByTopic } from '@/services/api';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import NewsContent from '@/components/news/NewsContent';
import Loading from '@/components/common/Loading';

// Configure ISR (Incremental Static Regeneration)
export const revalidate = 600; // Revalidate this page every 10 minutes

interface HomePageProps {
  searchParams: {
    category?: string;
  };
}

export default async function HomePage({ searchParams }: HomePageProps) {
  // Get the category from URL query params with a default of "Vše"
  const activeCategory = searchParams.category || "Vše";
  
  // Fetch data on the server
  const topicsData = await fetchTopics();
  const categories = ["Vše", ...topicsData.map(topic => topic.name)];
  
  // Fetch the appropriate news data based on selected category
  let newsData;
  if (activeCategory === "Vše") {
    newsData = await fetchLatestNews(20);
  } else {
    const selectedTopic = topicsData.find(topic => topic.name === activeCategory);
    if (selectedTopic) {
      newsData = await fetchNewsByTopic(selectedTopic.id);
    } else {
      newsData = [];
    }
  }

  // Note: The onSelectCategory callback is not needed here since the client-side 
  // navigation is handled directly in the CategoryNav component with the useRouter hook.
  // This is a server component, so it will re-render with the new searchParams when the URL changes.
  
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header 
        categories={categories} 
        activeCategory={activeCategory} 
      />
      
      <Suspense fallback={<Loading />}>
        <main className="max-w-6xl mx-auto px-4 py-6 w-full flex-grow">
          <NewsContent 
            news={newsData} 
            activeCategory={activeCategory} 
          />
        </main>
      </Suspense>
      
      <Footer 
        categories={categories} 
      />
    </div>
  );
}