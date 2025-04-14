/**
 * Site header component with title and category navigation
 */
import CategoryNav from '@/components/news/CategoryNav';

interface HeaderProps {
  /** List of all available categories */
  categories: string[];
  /** Currently selected category */
  activeCategory: string;
  /** Optional callback function when a category is selected */
  onSelectCategory?: (category: string) => void;
}

export default function Header({ 
  categories, 
  activeCategory, 
  onSelectCategory 
}: HeaderProps) {
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