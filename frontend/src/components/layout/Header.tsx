// components/layout/Header-alternative.tsx
"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import CategoryNav from "../news/CategoryNav";
import Script from "next/script";
import { searchNews } from "~/services/api";

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

interface SearchResult {
  id: string;
  title: string;
  url: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showSearchInput, setShowSearchInput] = useState(false); // Toggle for mobile
  const searchRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Debounce search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    setIsSearching(true);

    const timer = setTimeout(async () => {
      try {
        const response = await searchNews(searchQuery);
        setSearchResults(response || []);
        setShowResults(true);
      } catch (error) {
        console.error("Search error:", error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Close results when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setShowResults(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && searchQuery.trim()) {
      setShowResults(false);
      router.push(`/search/?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-gray-800 text-white shadow-lg">
      <Script
        id="Cookiebot"
        src="https://consent.cookiebot.com/uc.js"
        data-cbid="5de9e490-d9f4-41ae-95c1-69415eca43ff"
        data-blockingmode="auto"
        strategy="beforeInteractive"
      />
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex items-center justify-between gap-4 py-5">
          <Link
            href="/"
            className="text-2xl sm:text-3xl font-bold text-white transition-colors hover:text-red-400 flex-shrink-0"
          >
            Tvůj Novinář
          </Link>

          <div className="hidden md:flex items-center flex-1">
            {/* Delimiter before CategoryNav */}
            <div className="w-px h-6 bg-gray-500 opacity-50 mx-4"></div>
            <CategoryNav
              categories={categories}
              activeCategory={activeCategory}
            />
          </div>

          {/* Desktop search - always visible */}
          <div className="hidden sm:block relative w-48 md:w-64 flex-shrink-0" ref={searchRef}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => searchResults.length > 0 && setShowResults(true)}
              placeholder="Hledat články..."
              className="w-full rounded-lg bg-gray-700 px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-400"
            />
            
            {isSearching && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-white"></div>
              </div>
            )}

            {showResults && searchResults.length > 0 && (
              <div className="absolute left-0 right-0 top-full mt-2 max-h-96 overflow-y-auto rounded-lg bg-white shadow-xl z-50">
                {searchResults.map((result) => (
                  <Link
                    key={result.id}
                    href={`/article/${result.id}`}
                    onClick={() => {
                      setShowResults(false);
                      setSearchQuery("");
                    }}
                    className="block border-b border-gray-200 px-4 py-3 text-gray-800 transition-colors hover:bg-gray-100 last:border-b-0"
                  >
                    <h3 className="font-medium">{result.title}</h3>
                  </Link>
                ))}
              </div>
            )}

            {showResults && searchQuery && !isSearching && searchResults.length === 0 && (
              <div className="absolute left-0 right-0 top-full mt-2 rounded-lg bg-white p-4 text-center text-gray-600 shadow-xl">
                Žádné výsledky nenalezeny
              </div>
            )}
          </div>

          {/* Mobile search button */}
          <button
            onClick={() => setShowSearchInput(!showSearchInput)}
            className="sm:hidden p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
            aria-label="Hledat"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {showSearchInput ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile search input - collapsible */}
        {showSearchInput && (
          <div className="pb-4 sm:hidden" ref={searchRef}>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => searchResults.length > 0 && setShowResults(true)}
                placeholder="Hledat články..."
                className="w-full rounded-lg bg-gray-700 px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-400"
                autoFocus
              />
              
              {isSearching && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-white"></div>
                </div>
              )}

              {showResults && searchResults.length > 0 && (
                <div className="absolute left-0 right-0 top-full mt-2 max-h-96 overflow-y-auto rounded-lg bg-white shadow-xl z-50">
                  {searchResults.map((result) => (
                    <Link
                      key={result.id}
                      href={`/article/${result.id}`}
                      onClick={() => {
                        setShowResults(false);
                        setSearchQuery("");
                        setShowSearchInput(false);
                      }}
                      className="block border-b border-gray-200 px-4 py-3 text-gray-800 transition-colors hover:bg-gray-100 last:border-b-0"
                    >
                      <h3 className="font-medium text-sm">{result.title}</h3>
                    </Link>
                  ))}
                </div>
              )}

              {showResults && searchQuery && !isSearching && searchResults.length === 0 && (
                <div className="absolute left-0 right-0 top-full mt-2 rounded-lg bg-white p-4 text-center text-gray-600 shadow-xl text-sm">
                  Žádné výsledky nenalezeny
                </div>
              )}
            </div>
          </div>
        )}

        {/* Mobile navigation */}
        <div className="pb-4 md:hidden">
          <CategoryNav
            categories={categories}
            activeCategory={activeCategory}
          />
        </div>
        
      </div>
    </header>
  );
}