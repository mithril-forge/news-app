// components/layout/Header.tsx
'use client'

import Link from 'next/link';
import CategoryNav from '../news/CategoryNav';

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  return (
    <header className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="text-3xl font-bold text-red-600 hover:text-red-700 transition-colors">
            ZPRÁVY.CZ
          </Link>
          <nav className="hidden md:block">
            <CategoryNav 
              categories={categories} 
              activeCategory={activeCategory} 
            />
          </nav>
        </div>
        {/* Mobile navigation */}
        <div className="md:hidden pb-4">
          <CategoryNav 
            categories={categories} 
            activeCategory={activeCategory} 
          />
        </div>
      </div>
    </header>
  );
}