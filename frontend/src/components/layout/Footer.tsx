'use client'

/**
 * Site footer component with categories and contact information
 */
import { useRouter } from 'next/navigation';

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
    // Scroll to top for better UX
    window.scrollTo(0, 0);
    
    // Always navigate to home with the selected category
    if (category === 'Vše') {
      router.push('/');
    } else {
      router.push(`/?category=${encodeURIComponent(category)}`);
    }
    
    // Call callback if provided
    if (onSelectCategory) {
      onSelectCategory(category);
    }
  };

  return (
    <footer className="bg-gray-800 text-white py-8 mt-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-bold mb-4">ZPRÁVY.CZ</h3>
            <p className="text-gray-300 text-sm">
              Váš spolehlivý zdroj nejnovějších zpráv z České republiky i ze světa.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-bold mb-4">Kategorie</h3>
            <ul className="space-y-2">
              {categories.slice(1, 6).map(category => ( // Show first 5 categories except "Vše"
                <li key={category}>
                  <button
                    onClick={() => handleCategoryClick(category)}
                    className="text-gray-300 hover:text-white text-sm text-left"
                  >
                    {category}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-bold mb-4">Kontakt</h3>
            <p className="text-gray-300 text-sm">
              Email: info@zpravy.cz<br />
              Telefon: +420 123 456 789<br />
              Adresa: Václavské náměstí 1, Praha 1
            </p>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-gray-400">
          © {new Date().getFullYear()} ZPRÁVY.CZ - Všechna práva vyhrazena
        </div>
      </div>
    </footer>
  );
}