'use client'

/**
 * Navigation component for category/topic selection
 * Client component to handle user interactions
 */

interface CategoryNavProps {
  /** List of all available categories */
  categories: string[];
  /** Currently selected category */
  activeCategory: string;
  /** Callback function when a category is selected */
  onSelectCategory: (category: string) => void;
}

export default function CategoryNav({ 
  categories, 
  activeCategory, 
  onSelectCategory 
}: CategoryNavProps) {
  return (
    <nav className="overflow-x-auto pb-2">
      <ul className="flex space-x-6 whitespace-nowrap">
        {categories.map(category => (
          <li key={category}>
            <button
              onClick={() => onSelectCategory(category)}
              className={`text-sm font-medium transition-colors ${
                activeCategory === category
                  ? "text-red-600 border-b-2 border-red-600 pb-1"
                  : "text-gray-700 hover:text-red-600 pb-1"
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