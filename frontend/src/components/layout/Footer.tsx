import Link from 'next/link';
import { Separator } from '~/components/ui/separator';
import { Mail } from 'lucide-react';

interface FooterProps {
  categories: string[];
  onSelectCategory?: (category: string) => void;
}

export default function Footer({ categories, onSelectCategory }: FooterProps) {
  return (
    <footer className="w-full border-t bg-background mt-12">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          {/* Links */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <Link href="/about" className="hover:text-foreground transition-colors">
              O nás
            </Link>
            <Separator orientation="vertical" className="h-4" />
            <a
              href="mailto:info@tvujnovinar.cz"
              className="flex items-center gap-1.5 hover:text-foreground transition-colors"
            >
              <Mail className="h-3.5 w-3.5" />
              info@tvujnovinar.cz
            </a>
          </div>

          {/* Copyright */}
          <div className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Tvůj Novinář
          </div>
        </div>
      </div>
    </footer>
  );
}
