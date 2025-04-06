// src/app/article/[id]/page.tsx  <- Correct path for App Router
'use client' // Keep this because we use hooks (useState, useParams, useRouter)

import React from 'react';
// Import hooks from 'next/navigation' for App Router Client Components
import { useRouter, useParams } from 'next/navigation';
// Remove Head from 'next/head' - not used in App Router
// import Head from 'next/head';
import Image from 'next/image';
import Link from 'next/link';

// Adjust import paths relative to src/app/article/[id]/
import { initialNews, categories } from '../../../data/newData'; // Assuming data is in src/data
import Header from '../../../components/Layout/Header';       // Assuming components are in src/components
import Footer from '../../../components/Layout/Footer';       // Assuming components are in src/component
// Note: Metadata (title, description) should be handled via generateMetadata
// export function generateMetadata({ params }: { params: { id: string } }) { ... }
// This cannot be done directly within a Client Component.

function ArticlePage() {
  // Get router instance for navigation methods (like push)
  const router = useRouter();
  // Get route parameters using useParams()
  const params = useParams();
  // Extract the id. Ensure it's treated as a string. It might be string[] if using catch-all routes, but here it's string.
  const id = typeof params.id === 'string' ? params.id : undefined;

  // State for category navigation (remains the same)
  const [activeCategory, setActiveCategory] = React.useState("Vše");

  // Find the article - Now done after getting id from params
  // No need for router.isReady check here, params are available earlier
  const article = id
    ? initialNews.find(item => item.id.toString() === id)
    : null;

  // Handler for category selection (remains the same)
  const handleSelectCategory = (category: string) => { // Add type annotation
    setActiveCategory(category);
    router.push(`/?category=${category}`); // Use router for navigation
  };

  // --- Loading state is less common this way, as params are usually ready ---
  // If you were fetching data async based on id, you'd have a loading state here.
  // With static data, the main check is if the article was found.

   if (!id) {
     // Handle case where ID might not be available yet (though useParams usually resolves faster)
     // Or if the param wasn't a string.
     return (
        <div className="min-h-screen bg-gray-100 flex flex-col">
            <Header categories={categories} activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />
            <main className="max-w-3xl mx-auto px-4 py-12 flex-grow text-center"><p>Načítání ID...</p></main>
            <Footer categories={categories} onSelectCategory={handleSelectCategory} />
        </div>
     );
   }

   // Article Not Found Check
   if (!article) {
      return ( // Not Found state
            <div className="min-h-screen bg-gray-100 flex flex-col">
                {/* Removed Head component */}
                <Header categories={categories} activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />
                <main className="max-w-3xl mx-auto px-4 py-12 flex-grow text-center">
                    {/* <Head><title>Článek nenalezen</title></Head> <-- Remove */}
                    <h1 className="text-2xl font-bold text-gray-700">404 - Článek nenalezen</h1>
                    <p className="text-gray-500 mt-4">Omlouváme se, ale článek s ID '{id}' neexistuje.</p>
                    <Link href="/" className="mt-6 inline-block px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                        Zpět na hlavní stránku
                    </Link>
                </main>
                <Footer categories={categories} onSelectCategory={handleSelectCategory} />
           </div>
      );
  }


  // --- Render the Article Page ---
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
       {/* Removed Head component - Title/Desc should be set via Metadata API */}
      {/* <Head>...</Head> <-- Remove */}

      <Header
        categories={categories}
        activeCategory={article.category} // Highlight article's category
        onSelectCategory={handleSelectCategory}
      />

      <main className="max-w-3xl mx-auto px-4 py-8 w-full flex-grow">
        <article>
          <div className="mb-4 text-sm text-gray-600">
            <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">
              {article.category}
            </span>
            <span>{article.date}</span>
          </div>

          {/* Use article title for H1 - okay here */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
            {article.title}
          </h1>

          <div className="mb-8 relative w-full aspect-video bg-gray-200 rounded overflow-hidden">
             <Image
                src={article.image}
                alt={article.title}
                fill={true} // Use fill instead of layout="fill" in newer Next.js
                style={{objectFit:"cover"}} // Use style object for objectFit
                priority
             />
          </div>

          <div className="prose prose-lg max-w-none text-gray-700 whitespace-pre-wrap">
            {article.content}
          </div>


          <div className="mt-8 pt-4 border-t border-gray-200">
            <span className="text-gray-500 text-sm mr-2">Štítky:</span>
            {article.tags.map(tag => (
              <span key={tag} className="inline-block text-xs bg-gray-100 px-2 py-1 rounded mr-2 mb-2">
                {tag}
              </span>
            ))}
          </div>

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