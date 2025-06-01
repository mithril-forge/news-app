'use client'

/**
 * Navigation component for category/topic selection
 * Client component to handle user interactions
 */
import { useRouter, usePathname } from 'next/navigation';

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
  const router = useRouter();
  const pathname = usePathname();

  /**
   * Handles category selection and updates URL
   * @param category - The selected category
   */
  const handleCategorySelect = (category: string) => {
    // Navigate to home page with selected category
    // If we're already on the home page, just update query params
    // Otherwise, navigate completely to the home page with the category
    
    if (category === 'Vše') {
      // Always navigate to home with no params for the default category
      router.push('/');
    } else {
      // For other categories, include the category in the URL
      router.push(`/?category=${encodeURIComponent(category)}`);
    }

    // If callback provided, call it as well
    if (onSelectCategory) {
      onSelectCategory(category);
    }
  };

  return (
    <nav className="overflow-x-auto pb-2">
      <ul className="flex space-x-6 whitespace-nowrap">
        {categories.map(category => (
          <li key={category}>
            <button
              onClick={() => handleCategorySelect(category)}
              className={`text-sm font-medium transition-colors ${
                activeCategory === category
                  ? "text-red-400 border-b-2 border-red-400 pb-1"
                  : "text-gray-300 hover:text-red-400 pb-1"
              }`}
              aria-current={activeCategory === category ? 'page' : undefined}
            >
              {category}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}