'use client'

import React, { useRef, useState, useEffect } from 'react';
import Link from 'next/link';
import { Badge } from '~/components/ui/badge';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '~/components/ui/button';
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
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftFade, setShowLeftFade] = useState(false);
  const [showRightFade, setShowRightFade] = useState(false);

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

  const checkScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftFade(scrollLeft > 10);
      setShowRightFade(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = direction === 'left' ? -200 : 200;
      scrollRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    checkScroll();
    const currentRef = scrollRef.current;
    if (currentRef) {
      currentRef.addEventListener('scroll', checkScroll);
      window.addEventListener('resize', checkScroll);
    }
    return () => {
      if (currentRef) {
        currentRef.removeEventListener('scroll', checkScroll);
      }
      window.removeEventListener('resize', checkScroll);
    };
  }, [categories]);

  // Filter out AI Feed from the regular nav (shown in header separately)
  const visibleCategories = categories.filter(c => c !== 'AI Feed');

  return (
    <nav className="relative group">
      {/* Left fade indicator */}
      {showLeftFade && (
        <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
      )}

      {/* Right fade indicator */}
      {showRightFade && (
        <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
      )}

      {/* Left scroll button */}
      {showLeftFade && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute left-0 top-1/2 -translate-y-1/2 z-20 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
          onClick={() => scroll('left')}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      )}

      {/* Right scroll button */}
      {showRightFade && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-0 top-1/2 -translate-y-1/2 z-20 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
          onClick={() => scroll('right')}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      )}

      {/* Scrollable categories */}
      <div
        ref={scrollRef}
        className="overflow-x-auto scrollbar-hide scroll-smooth"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <div className="flex items-center gap-2 min-w-max px-1 py-1">
          {visibleCategories.map((category) => {
            const isActive = activeCategory === category;

            return (
              <Link
                key={category}
                href={getCategoryUrl(category)}
                onClick={() => handleCategoryClick(category)}
                aria-current={isActive ? 'page' : undefined}
                className="flex-shrink-0"
              >
                <Badge
                  variant={isActive ? 'default' : 'outline'}
                  className={cn(
                    'cursor-pointer transition-all hover:scale-105',
                    isActive && 'shadow-sm'
                  )}
                >
                  {category}
                </Badge>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
