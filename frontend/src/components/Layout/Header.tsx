// src/components/Layout/Header.js
import React from 'react';
import CategoryNav from '../News/CategoryNav'; // Adjust path as needed

function Header({ categories, activeCategory, onSelectCategory }) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4">
        <div className="py-4">
          <h1 className="text-3xl font-bold text-gray-800">ZPRÁVY.CZ</h1>
          <p className="text-sm text-gray-500">NAVŽDY BEZ REKLAM</p>
        </div>
        <CategoryNav
          categories={categories}
          activeCategory={activeCategory}
          onSelectCategory={onSelectCategory}
        />
      </div>
    </header>
  );
}

export default Header;