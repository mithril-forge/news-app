'use client'

import Link from 'next/link';
import { Newspaper } from 'lucide-react';
import CategoryNav from '../news/CategoryNav';

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <Newspaper className="h-6 w-6 text-primary transition-transform group-hover:scale-110" />
            <span className="text-xl font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
              Tvůj Novinář
            </span>
          </Link>
          <nav className="hidden md:block">
            <CategoryNav
              categories={categories}
              activeCategory={activeCategory}
            />
          </nav>
        </div>
        {/* Mobile navigation */}
        <div className="md:hidden pb-3">
          <CategoryNav
            categories={categories}
            activeCategory={activeCategory}
          />
        </div>
      </div>
    </header>
  );
}