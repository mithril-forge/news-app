'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';

// Import API service
import { fetchTopics, fetchLatestNews, fetchNewsByTopic } from '../services/api';

// Import Components
import Header from '../components/Layout/Header';
import Footer from '../components/Layout/Footer';
import FeaturedArticle from '../components/News/FeaturedArticle';
import ArticleCard from '../components/News/ArticleCard';

export default function Home() {
  // State for news and topics
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("Vše");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch topics and latest news on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);

        // Fetch topics (categories)
        const topicsData = await fetchTopics();
        // Add "Vše" (All) category
        setCategories(["Vše", ...topicsData.map(topic => topic.name)]);

        // Fetch latest news
        const latestNews = await fetchLatestNews(20); // Adjust count as needed
        setNews(latestNews);
        setFilteredNews(latestNews);

        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch initial data:", err);
        setError("Failed to load data. Please try again later.");
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // Handler for category selection
  const handleSelectCategory = async (category) => {
    setActiveCategory(category);
    setLoading(true);

    try {
      if (category === "Vše") {
        setFilteredNews(news);
      } else {
        // Find topic ID from the category name
        const topicData = await fetchTopics();
        const selectedTopic = topicData.find(topic => topic.name === category);

        if (selectedTopic) {
          const topicNews = await fetchNewsByTopic(selectedTopic.id);
          setFilteredNews(topicNews);
        } else {
          setFilteredNews([]);
        }
      }
    } catch (err) {
      console.error(`Error filtering by category ${category}:`, err);
      setError(`Failed to load articles for ${category}`);
    } finally {
      setLoading(false);
      window.scrollTo(0, 0); // Scroll to top on category change
    }
  };

  // Derived state for rendering
  const featuredArticle = filteredNews.length > 0 ? filteredNews[0] : null;
  const remainingArticles = filteredNews.slice(1);

  // Show loading state
  if (loading && news.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col">
        <Header
          categories={categories}
          activeCategory={activeCategory}
          onSelectCategory={handleSelectCategory}
        />
        <main className="max-w-6xl mx-auto px-4 py-6 w-full flex-grow flex items-center justify-center">
          <div className="text-center">
            <p className="text-xl">Načítání zpráv...</p>
          </div>
        </main>
        <Footer
          categories={categories}
          onSelectCategory={handleSelectCategory}
        />
      </div>
    );
  }

  // Show error state
  if (error && news.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col">
        <Header
          categories={categories}
          activeCategory={activeCategory}
          onSelectCategory={handleSelectCategory}
        />
        <main className="max-w-6xl mx-auto px-4 py-6 w-full flex-grow flex items-center justify-center">
          <div className="text-center bg-red-50 p-6 rounded-lg border border-red-200">
            <p className="text-red-600">{error}</p>
            <button
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              onClick={() => window.location.reload()}
            >
              Zkusit znovu
            </button>
          </div>
        </main>
        <Footer
          categories={categories}
          onSelectCategory={handleSelectCategory}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Head>
        <title>ZPRÁVY.CZ - Aktuální zprávy z ČR i ze světa</title>
        <meta name="description" content="Nejnovější zprávy z České republiky a ze světa" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header
        categories={categories}
        activeCategory={activeCategory}
        onSelectCategory={handleSelectCategory}
      />

      <main className="max-w-6xl mx-auto px-4 py-6 w-full flex-grow">
        {loading && (
          <div className="text-center py-4">
            <p>Načítání...</p>
          </div>
        )}

        {error && activeCategory !== "Vše" && (
          <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-lg">
            {error}
          </div>
        )}

        {featuredArticle && <FeaturedArticle article={featuredArticle} />}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {remainingArticles.length > 0 ? (
            remainingArticles.map(item => (
              <ArticleCard key={item.id} item={item} />
            ))
          ) : (
            activeCategory !== "Vše" && featuredArticle && (
              <div className="md:col-span-3 text-center py-12">
                <p className="text-gray-500">Žádné další články v kategorii '{activeCategory}'</p>
              </div>
            )
          )}

          {filteredNews.length === 0 && activeCategory !== "Vše" && (
            <div className="md:col-span-3 text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">Žádné články nebyly nalezeny v kategorii '{activeCategory}'</p>
            </div>
          )}
        </div>
      </main>

      <Footer
        categories={categories}
        onSelectCategory={handleSelectCategory}
      />
    </div>
  );
}