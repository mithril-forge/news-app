'use client'

/**
 * Simple footer component matching the emoji theme
 */
import { useRouter } from 'next/navigation';
import { getCategoryEmoji } from '@/lib/categoryEmoji';

interface FooterProps {
  /** List of all available categories */
  categories: string[];
  /** Optional callback for category selection */
  onSelectCategory?: (category: string) => void;
}

export default function Footer({ 
  categories, 
  onSelectCategory 
}: FooterProps) {
  const router = useRouter();

  /**
   * Handles category selection with scroll to top
   * @param category - Selected category name
   */
  const handleCategoryClick = (category: string) => {
    window.scrollTo(0, 0);
    
    if (category === 'Vše') {
      router.push('/');
    } else {
      router.push(`/?category=${encodeURIComponent(category)}`);
    }
    
    if (onSelectCategory) {
      onSelectCategory(category);
    }
  };

  return (
    <footer className="bg-gray-800 text-white py-8 mt-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🤖</span>
              <h3 className="text-xl font-bold">NOVINAR.AI</h3>
            </div>
            <p className="text-gray-300 text-sm">
              Váš digitální zpravodaj čte za vás všechna česká média a vybírá jen klíčové události dne.
            </p>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-lg font-bold mb-4">Kategorie</h3>
            <div className="space-y-2">
              {categories.slice(1, 6).map(category => {
                  const categoryInfo = getCategoryEmoji(category?.name || 'Vše');
                  return (
                  <button
                    key={category}
                    onClick={() => handleCategoryClick(category)}
                    className="flex items-center gap-2 text-gray-300 hover:text-white text-sm transition-colors"
                  >
                    <span>{categoryInfo.emoji}</span>
                    <span>{category}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-lg font-bold mb-4">Kontakt</h3>
            <div className="text-gray-300 text-sm space-y-2">
              <div className="flex items-center gap-2">
                <span>📧</span>
                <span>ainovinar@gmail.com</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🔄</span>
                <span>Aktualizace každých 10 minut</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-gray-400">
          <div className="flex items-center justify-center gap-1">
            <span>🤖</span>
            <span>© {new Date().getFullYear()} NOVINAR.AI - Všechna práva vyhrazena</span>
          </div>
        </div>
      </div>
    </footer>
  );
}