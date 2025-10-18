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
      {/* Remove individual flex containers and put everything in one line */}
      <div className="flex items-center gap-3 text-sm flex-wrap justify-center">
        <Link
          href="/about"
          className="text-gray-300 hover:text-white transition-colors"
        >
          O nás
        </Link>
        
        <span className="text-gray-600">•</span>
        
        <Link
          href="/terms"
          className="text-gray-300 hover:text-white transition-colors"
        >
          Zásady ochrany osobních údajů
        </Link>
        
        <span className="text-gray-600">•</span>
        
        <Link
          href="/cookie-policy"
          className="text-gray-300 hover:text-white transition-colors"
        >
          Zásady používání cookies
        </Link>
        
        <span className="text-gray-600">•</span>
        
        <a 
          href="mailto:info@tvujnovinar.cz"
          className="text-gray-300 hover:text-white transition-colors"
        >
          info@tvujnovinar.cz
        </a>
      </div>
      
      <div className="text-sm text-gray-400">
        © {new Date().getFullYear()} Tvůj Novinář
      </div>
    </div>
  </div>
</footer>
  );
}