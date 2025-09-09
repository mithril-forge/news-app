'use client'

/**
 * Navigation component for category/topic selection
 * Client component to handle user interactions
 */
import React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

interface CategoryNavProps {
  /** List of all available categories */
  categories: string[];
  /** Currently selected category */
  activeCategory: string;
  /** Optional callback function when a category is selected */
  onSelectCategory?: (category: string) => void;
}

export default function CategoryNav({
  categories,
  activeCategory,
  onSelectCategory
}: CategoryNavProps) {
  const pathname = usePathname();

  /**
   * Get the appropriate URL for each category
   * @param category - The category name
   * @returns The URL path for that category
   */
  const getCategoryUrl = (category: string): string => {
    // Handle special "AI Feed" category
    if (category === 'AI Feed') {
      return '/feed';
    } else if (category === 'Vše') {
      // Always navigate to home with no params for the default category
      return '/';
    } else {
      // For other categories, include the category in the URL
      return `/?category=${encodeURIComponent(category)}`;
    }
  };

  /**
   * Handle optional callback when category is clicked
   * @param category - The selected category
   */
  const handleCategoryClick = (category: string) => {
    // If callback provided, call it
    if (onSelectCategory) {
      onSelectCategory(category);
    }
  };

  return (
    <nav className="overflow-x-auto pb-2">
      <ul className="flex items-center whitespace-nowrap">
        {categories.map((category, index) => {
          // Special styling for AI Feed
          const isAIFeed = category === 'AI Feed';
          const isFirstRegularCategory = !isAIFeed && categories[index - 1] === 'AI Feed';

          if (isAIFeed) {
            return (
              <li key={category}>
                <Link
                  href={getCategoryUrl(category)}
                  onClick={() => handleCategoryClick(category)}
                  className={`inline-flex items-center space-x-1 text-sm font-medium transition-colors hover:cursor-pointer ${
                    activeCategory === category
                      ? "text-blue-400 border-b-2 border-blue-400 pb-1"
                      : "text-blue-300 hover:text-blue-400 pb-1"
                  }`}
                  aria-current={activeCategory === category ? 'page' : undefined}
                >
                  <span className="text-sm">🧠</span>
                  <span>{category}</span>
                </Link>
              </li>
            );
          }

          // Add divider before first regular category
          if (isFirstRegularCategory) {
            return (
              <React.Fragment key={category}>
                <li className="mx-4">
                  <div className="w-px h-4 bg-gray-500 opacity-50"></div>
                </li>
                <li className="mr-6">
                  <Link
                    href={getCategoryUrl(category)}
                    onClick={() => handleCategoryClick(category)}
                    className={`text-sm font-medium transition-colors hover:cursor-pointer ${
                      activeCategory === category
                        ? "text-red-400 border-b-2 border-red-400 pb-1"
                        : "text-gray-300 hover:text-red-400 pb-1"
                    }`}
                    aria-current={activeCategory === category ? 'page' : undefined}
                  >
                    {category}
                  </Link>
                </li>
              </React.Fragment>
            );
          }

          // Regular category styling
          return (
            <li key={category} className="mr-6">
              <Link
                href={getCategoryUrl(category)}
                onClick={() => handleCategoryClick(category)}
                className={`text-sm font-medium transition-colors hover:cursor-pointer ${
                  activeCategory === category
                    ? "text-red-400 border-b-2 border-red-400 pb-1"
                    : "text-gray-300 hover:text-red-400 pb-1"
                }`}
                aria-current={activeCategory === category ? 'page' : undefined}
              >
                {category}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
