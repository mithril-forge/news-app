import Link from 'next/link';
import { Separator } from '~/components/ui/separator';
import { Badge } from '~/components/ui/badge';
import { Mail, Sparkles, Newspaper, Heart } from 'lucide-react';

interface FooterProps {
  categories: string[];
  onSelectCategory?: (category: string) => void;
}

export default function Footer({ categories, onSelectCategory }: FooterProps) {
  return (
    <footer className="w-full border-t bg-background/50 backdrop-blur-sm mt-16 relative">
      {/* Gradient accent line */}
      <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand Section */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
                <Newspaper className="h-4 w-4 text-primary" />
              </div>
              <span className="font-bold text-lg">Tvůj Novinář</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Tvůj spolehlivý zdroj nejnovějších zpráv z České republiky i ze světa.
            </p>
            <Badge variant="secondary" className="gap-1.5">
              <Sparkles className="h-3 w-3" />
              <span className="text-xs">Powered by AI</span>
            </Badge>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">
              Navigace
            </h3>
            <div className="flex flex-col gap-2">
              <Link
                href="/"
                className="text-sm hover:text-primary transition-colors w-fit"
              >
                Domovská stránka
              </Link>
              <Link
                href="/feed"
                className="text-sm hover:text-primary transition-colors w-fit inline-flex items-center gap-1.5"
              >
                <Sparkles className="h-3 w-3" />
                AI Feed
              </Link>
              <Link
                href="/about"
                className="text-sm hover:text-primary transition-colors w-fit"
              >
                O nás
              </Link>
            </div>
          </div>

          {/* Contact */}
          <div className="space-y-3">
            <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">
              Kontakt
            </h3>
            <a
              href="mailto:info@tvujnovinar.cz"
              className="text-sm hover:text-primary transition-colors flex items-center gap-2 w-fit"
            >
              <Mail className="h-4 w-4" />
              info@tvujnovinar.cz
            </a>
          </div>
        </div>

        <Separator className="my-6" />

        {/* Bottom section */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span>© {new Date().getFullYear()} Tvůj Novinář</span>
            <span>•</span>
            <span className="inline-flex items-center gap-1">
              Vytvořeno s <Heart className="h-3 w-3 fill-destructive text-destructive animate-pulse" /> v Česku
            </span>
          </div>
          <div className="text-xs">
            Agregátor zpráv využívající umělou inteligenci
          </div>
        </div>
      </div>
    </footer>
  );
}
