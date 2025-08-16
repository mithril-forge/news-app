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
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          {/* Links */}
          <div className="flex items-center gap-6 text-sm">
            <Link
              href="/about"
              className="text-gray-300 hover:text-white transition-colors"
            >
              O nás
            </Link>
            <span className="text-gray-500">|</span>
            <span className="text-gray-300">info@tvujnovinar.cz</span>
          </div>

          {/* Copyright */}
          <div className="text-sm text-gray-400">
            © {new Date().getFullYear()} Tvůj Novinář
          </div>
        </div>
      </div>
    </footer>
  );
}
