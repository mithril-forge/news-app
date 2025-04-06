// src/components/News/CategoryNav.js
import React from 'react';

function CategoryNav({ categories, activeCategory, onSelectCategory }) {
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
            >
              {category}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default CategoryNav;