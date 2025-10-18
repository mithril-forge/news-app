// components/layout/Header.tsx
"use client";

import Link from "next/link";
import CategoryNav from "../news/CategoryNav";
import Script from "next/script";

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-gray-800 text-white shadow-lg">
      <Script
        id="Cookiebot"
        src="https://consent.cookiebot.com/uc.js"
        data-cbid="5de9e490-d9f4-41ae-95c1-69415eca43ff"
        data-blockingmode="auto" // ← AUTO mode
        strategy="beforeInteractive"
      />
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex items-center justify-between py-4">
          <Link
            href="/"
            className="text-3xl font-bold text-white transition-colors hover:text-red-400"
          >
            Tvůj Novinář
          </Link>
          <nav className="hidden md:block">
            <CategoryNav
              categories={categories}
              activeCategory={activeCategory}
            />
          </nav>
        </div>
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
