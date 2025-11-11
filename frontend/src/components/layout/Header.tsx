// components/layout/Header.tsx
"use client";

import Link from "next/link";
import { useState } from "react";
import CategoryNav from "../news/CategoryNav";
import Script from "next/script";
import SearchInput from "../search/SearchInput";
import MobileSearchInput from "../search/MobileSearchInput";
import SearchToggleButton from "../search/SearchToggleButton";
import { useSearch } from "../search/useSearch";

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  const [showSearchInput, setShowSearchInput] = useState(false);
  
  const {
    searchQuery,
    setSearchQuery,
    searchResults,
    isSearching,
    showResults,
    setShowResults,
    handleKeyDown,
    handleResultClick,
  } = useSearch();

  const handleMobileResultClick = () => {
    handleResultClick();
    setShowSearchInput(false);
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
          <SearchInput
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            searchResults={searchResults}
            isSearching={isSearching}
            showResults={showResults}
            setShowResults={setShowResults}
            onResultClick={handleResultClick}
            onKeyDown={handleKeyDown}
            className="hidden sm:block w-48 md:w-64 flex-shrink-0"
          />

          {/* Mobile search toggle button */}
          <SearchToggleButton
            isOpen={showSearchInput}
            onClick={() => setShowSearchInput(!showSearchInput)}
          />
        </div>

        {/* Mobile search input - collapsible */}
        {showSearchInput && (
          <MobileSearchInput
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            searchResults={searchResults}
            isSearching={isSearching}
            showResults={showResults}
            setShowResults={setShowResults}
            onResultClick={handleMobileResultClick}
            onKeyDown={handleKeyDown}
          />
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