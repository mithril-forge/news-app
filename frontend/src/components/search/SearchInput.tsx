// components/search/SearchInput.tsx
"use client";

import { useRef, useEffect } from "react";
import Link from "next/link";

interface SearchResult {
  id: string;
  title: string;
  url: string;
}

interface SearchInputProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchResults: SearchResult[];
  isSearching: boolean;
  showResults: boolean;
  setShowResults: (show: boolean) => void;
  onResultClick: () => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
}

export default function SearchInput({
  searchQuery,
  setSearchQuery,
  searchResults,
  isSearching,
  showResults,
  setShowResults,
  onResultClick,
  onKeyDown,
  placeholder = "Hledat články...",
  className = "",
}: SearchInputProps) {
  const searchRef = useRef<HTMLDivElement>(null);

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
  }, [setShowResults]);

  return (
    <div className={`relative ${className}`} ref={searchRef}>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onKeyDown={onKeyDown}
        onFocus={() => searchResults.length > 0 && setShowResults(true)}
        placeholder={placeholder}
        className="w-full rounded-lg bg-gray-700 px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-400"
      />

      {/* Loading indicator */}
      {isSearching && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-white"></div>
        </div>
      )}

      {/* Search results dropdown */}
      {showResults && searchResults.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 max-h-96 overflow-y-auto rounded-lg bg-white shadow-xl z-50">
          {searchResults.map((result) => (
            <Link
              key={result.id}
              href={`/article/${result.id}`}
              onClick={onResultClick}
              className="block border-b border-gray-200 px-4 py-3 text-gray-800 transition-colors hover:bg-gray-100 last:border-b-0"
            >
              <h3 className="font-medium">{result.title}</h3>
            </Link>
          ))}
        </div>
      )}

      {/* No results message */}
      {showResults && searchQuery && !isSearching && searchResults.length === 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 rounded-lg bg-white p-4 text-center text-gray-600 shadow-xl">
          Žádné výsledky nenalezeny
        </div>
      )}
    </div>
  );
}