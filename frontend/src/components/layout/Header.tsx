'use client'

import { useState } from 'react';
import Link from 'next/link';
import { Newspaper, Menu, X, Sparkles } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '~/components/ui/sheet';
import { ScrollArea } from '~/components/ui/scroll-area';
import { Button } from '~/components/ui/button';
import { Separator } from '~/components/ui/separator';
import CategoryNav from '../news/CategoryNav';

interface HeaderProps {
  categories: string[];
  activeCategory: string;
}

export default function Header({ categories, activeCategory }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b glass">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20 transition-all group-hover:scale-110 group-hover:bg-primary/20">
              <Newspaper className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xl font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
              Tvůj Novinář
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-4">
            <CategoryNav
              categories={categories}
              activeCategory={activeCategory}
            />
            <Separator orientation="vertical" className="h-6" />
            <Button asChild size="sm" className="ai-gradient gap-2">
              <Link href="/feed">
                <Sparkles className="h-4 w-4" />
                AI Feed
              </Link>
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild className="lg:hidden">
              <Button variant="ghost" size="icon" aria-label="Open menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetHeader>
                <SheetTitle className="text-left flex items-center gap-2">
                  <Newspaper className="h-5 w-5 text-primary" />
                  Navigace
                </SheetTitle>
              </SheetHeader>

              <ScrollArea className="h-[calc(100vh-8rem)] mt-6">
                <div className="space-y-6">
                  {/* AI Feed CTA */}
                  <div className="ai-gradient-border rounded-lg p-4">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-10 h-10 rounded-lg ai-gradient flex items-center justify-center">
                        <Sparkles className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-sm mb-1">AI Feed</h3>
                        <p className="text-xs text-muted-foreground">
                          Personalizované zprávy jen pro tebe
                        </p>
                      </div>
                    </div>
                    <Button asChild className="w-full ai-gradient" onClick={() => setMobileMenuOpen(false)}>
                      <Link href="/feed">
                        Otevřít AI Feed
                      </Link>
                    </Button>
                  </div>

                  <Separator />

                  {/* Categories */}
                  <div>
                    <h3 className="font-semibold text-sm mb-3 text-muted-foreground uppercase tracking-wide">
                      Kategorie
                    </h3>
                    <div className="space-y-1">
                      {categories.filter(c => c !== 'AI Feed').map((category) => {
                        const isActive = activeCategory === category;
                        const href = category === 'Vše' ? '/' : `/?category=${encodeURIComponent(category)}`;

                        return (
                          <Link
                            key={category}
                            href={href}
                            onClick={() => setMobileMenuOpen(false)}
                            className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                              isActive
                                ? 'bg-primary text-primary-foreground'
                                : 'hover:bg-accent hover:text-accent-foreground'
                            }`}
                          >
                            {category}
                          </Link>
                        );
                      })}
                    </div>
                  </div>

                  <Separator />

                  {/* Additional Links */}
                  <div>
                    <h3 className="font-semibold text-sm mb-3 text-muted-foreground uppercase tracking-wide">
                      Ostatní
                    </h3>
                    <div className="space-y-1">
                      <Link
                        href="/about"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block px-3 py-2 rounded-lg text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
                      >
                        O nás
                      </Link>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>

        {/* Tablet Navigation (md to lg) */}
        <div className="hidden md:block lg:hidden pb-3">
          <CategoryNav
            categories={categories}
            activeCategory={activeCategory}
          />
        </div>
      </div>
    </header>
  );
}