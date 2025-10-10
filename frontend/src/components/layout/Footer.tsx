/**
 * Minimal footer component
 */
import Link from 'next/link';

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

  return (
    <footer className="bg-gray-800 text-white py-6 mt-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-2">
          {/* Links */}
          <div className="flex items-center gap-3 text-sm">
            <Link
              href="/about"
              className="text-gray-300 hover:text-white transition-colors"
            >
              O nás
            </Link>
          </div>
          
          <div className="flex items-center gap-3 text-sm">
            <Link
              href="/terms"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Zásady ochrany osobních údajů
            </Link>
          </div>
          
          <div className="flex items-center gap-3 text-sm">
            <Link
              href="/cookie-policy"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Zásady používání cookies
            </Link>
          </div>
          
          <span className="text-gray-500 text-sm">|</span>
          
          <a 
            href="mailto:info@tvujnovinar.cz"
            className="text-sm text-gray-300 hover:text-white transition-colors"
          >
            info@tvujnovinar.cz
          </a>
          
          <div className="text-sm text-gray-400">
            © {new Date().getFullYear()} Tvůj Novinář
          </div>
        </div>
      </div>
    </footer>
  );
}