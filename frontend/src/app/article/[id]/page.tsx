// src/app/article/[id]/page.tsx
'use client' // Keep this because we use hooks

// Import React hooks
import React, { useState, useEffect } from 'react';
// Import hooks from 'next/navigation' for App Router Client Components
import { useRouter, useParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

// Import API functions and types - Adjust path as needed
import { fetchNewsById, NewsArticle } from '../../../services/api';
// Assuming static categories are still used for Header/Footer
import { categories } from '../../../data/newData'; // Assuming data is in src/data
import Header from '../../../components/Layout/Header'; // Assuming components are in src/components
import Footer from '../../../components/Layout/Footer'; // Assuming components are in src/components

// Note: Metadata (title, description) should be handled via generateMetadata
// This cannot be done directly within a Client Component like this.

function ArticlePage() {
  const router = useRouter();
  const params = useParams();
  const id = typeof params.id === 'string' ? params.id : undefined;

  // --- State Hooks for API Data ---
  const [article, setArticle] = useState<NewsArticle | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // -----------------------------

  // State for category navigation (passed to Header/Footer)
  const [activeCategory, setActiveCategory] = useState("Vše");

  // --- Fetch Data Effect ---
  useEffect(() => {
    if (id) {
      setLoading(true);
      setError(null);
      fetchNewsById(id)
        .then(data => {
          setArticle(data); // API returns article object or null for 404
        })
        .catch(err => {
          console.error("Failed to fetch article:", err);
          setError(err.message || "Nastala chyba při načítání článku.");
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      // Handle case where ID is missing in params immediately
      setError("Článek nelze načíst: Chybí ID v adrese.");
      setLoading(false);
    }
  }, [id]); // Dependency array: re-fetch if id changes
  // -------------------------


  // --- Handler for category selection (unchanged) ---
  const handleSelectCategory = (category: string) => {
    setActiveCategory(category);
    router.push(`/?category=${category}`);
  };
  // -----------------------------------------------


  // --- Render Loading State ---
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col">
        <Header categories={categories} activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />
        <main className="max-w-3xl mx-auto px-4 py-12 flex-grow text-center">
          <p className="text-gray-500">Načítání článku...</p>
        </main>
        <Footer categories={categories} onSelectCategory={handleSelectCategory} />
      </div>
    );
  }
  // --------------------------


  // --- Render Error State ---
  if (error) {
     return (
        <div className="min-h-screen bg-gray-100 flex flex-col">
            <Header categories={categories} activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />
            <main className="max-w-3xl mx-auto px-4 py-12 flex-grow text-center">
                <h1 className="text-2xl font-bold text-red-600">Chyba</h1>
                <p className="text-gray-700 mt-4">{error}</p>
                <Link href="/" className="mt-6 inline-block px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                    Zpět na hlavní stránku
                </Link>
            </main>
            <Footer categories={categories} onSelectCategory={handleSelectCategory} />
        </div>
     );
   }
  // ------------------------


   // --- Render Article Not Found State (API returned null or fetch succeeded without data) ---
   // This check runs *after* loading is false and error is null
   if (!article) {
      return (
            <div className="min-h-screen bg-gray-100 flex flex-col">
                <Header categories={categories} activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />
                <main className="max-w-3xl mx-auto px-4 py-12 flex-grow text-center">
                    <h1 className="text-2xl font-bold text-gray-700">404 - Článek nenalezen</h1>
                    {/* Provide the ID if available */}
                    <p className="text-gray-500 mt-4">Omlouváme se, ale článek {id ? `s ID '${id}'` : ''} neexistuje nebo nemohl být načten.</p>
                    <Link href="/" className="mt-6 inline-block px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                        Zpět na hlavní stránku
                    </Link>
                </main>
                <Footer categories={categories} onSelectCategory={handleSelectCategory} />
           </div>
      );
  }
  // -----------------------------------------------------------------------------------------


  // --- Render the Article Page using data from the 'article' state variable ---
  // Set document title - less ideal for SEO than generateMetadata, but works on client-side
  if (typeof window !== 'undefined') {
      document.title = article.title;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header
        categories={categories}
        activeCategory={article.topic_name} // Highlight article's category from fetched data
        onSelectCategory={handleSelectCategory}
      />

      <main className="max-w-3xl mx-auto px-4 py-8 w-full flex-grow">
        <article>
          <div className="mb-4 text-sm text-gray-600">
            <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">
              {article.topic_name}
            </span>
            {/* Format date if needed */}
            <span>{new Date(article.updated_at).toLocaleDateString('cs-CZ')}</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
            {article.title}
          </h1>

          <div className="mb-8 relative w-full aspect-video bg-gray-200 rounded overflow-hidden">
             {/* Ensure article.image is a valid URL */}
             {article.image_url && (<Image
                src={article.image_url}
                alt={article.title}
                fill={true}
                style={{objectFit:"cover"}}
                priority // Keep if LCP element
             />)}
          </div>

          {/* Adjust rendering based on content format (plain text shown) */}
          <div className="prose prose-lg max-w-none text-gray-700 whitespace-pre-wrap">
            {article.content}
            {/* Or: <div dangerouslySetInnerHTML={{ __html: article.content }} /> if HTML */}
          </div>

          {/* Render tags only if they exist */}
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


            <div className="mt-8">
                <Link href="/" className="text-red-600 hover:text-red-800">
                    &larr; Zpět na přehled zpráv
                </Link>
            </div>

        </article>
      </main>

      <Footer
        categories={categories}
        onSelectCategory={handleSelectCategory}
      />
    </div>
  );
}

export default ArticlePage;