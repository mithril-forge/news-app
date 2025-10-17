'use client'

import React from 'react';
import Link from 'next/link';
import { Badge } from '~/components/ui/badge';
import { Brain } from 'lucide-react';
import { cn } from '~/lib/utils';

interface CategoryNavProps {
  categories: string[];
  activeCategory: string;
  onSelectCategory?: (category: string) => void;
}

export default function CategoryNav({
  categories,
  activeCategory,
  onSelectCategory
}: CategoryNavProps) {
  const getCategoryUrl = (category: string): string => {
    if (category === 'AI Feed') {
      return '/feed';
    } else if (category === 'Vše') {
      return '/';
    } else {
      return `/?category=${encodeURIComponent(category)}`;
    }
  };

  const handleCategoryClick = (category: string) => {
    if (onSelectCategory) {
      onSelectCategory(category);
    }
  };

  return (
    <nav className="overflow-x-auto">
      <div className="flex items-center gap-2 flex-wrap">
        {categories.map((category) => {
          const isActive = activeCategory === category;
          const isAIFeed = category === 'AI Feed';

          return (
            <Link
              key={category}
              href={getCategoryUrl(category)}
              onClick={() => handleCategoryClick(category)}
              aria-current={isActive ? 'page' : undefined}
            >
              <Badge
                variant={isActive ? 'default' : 'outline'}
                className={cn(
                  'cursor-pointer transition-colors',
                  isAIFeed && 'gap-1.5'
                )}
              >
                {isAIFeed && <Brain className="h-3 w-3" />}
                {category}
              </Badge>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
