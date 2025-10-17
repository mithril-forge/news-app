/**
 * InputNewsList server component for displaying input news sources with new design
 */
import Link from 'next/link';
import LogoWithFallback from '@/components/common/LogoWithFallback';
import { Card, CardContent } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { ExternalLink, User, Calendar, Newspaper } from 'lucide-react';

// Define the interface for InputNews objects
interface InputNewsDetailed {
  publication_date: string;
  title: string;
  author: string;
  source_site: string;
  source_url: string;
}

interface InputNewsListProps {
  inputNews: InputNewsDetailed[];
}

const InputNewsList = ({ inputNews }: InputNewsListProps) => {
  // Format the date to display in Czech format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('cs-CZ');
  };

  // Get logo URL for source site
  const getSourceLogo = (sourceSite: string): { url: string; fallback: string } => {
    const lowerSite = sourceSite.toLowerCase();
    
    // Czech news sites logo mapping
    const logoMap: { [key: string]: { url: string; fallback: string } } = {
      'aktuálně': { 
        url: 'https://cdn.xsd.cz/resize/ff7fdd7fdb1b3318adbdac55719cdf70_resize=2000,1125_.png?hash=0406a7ceea87f79c626d33bd3d5a4a9b',
        fallback: 'AK'
      },
      'aktualne': { 
        url: 'https://cdn.xsd.cz/resize/ff7fdd7fdb1b3318adbdac55719cdf70_resize=2000,1125_.png?hash=0406a7ceea87f79c626d33bd3d5a4a9b',
        fallback: 'AK'
      },
      'novinky': { 
        url: 'https://upload.wikimedia.org/wikipedia/commons/2/20/Novinky_logo.png',
        fallback: 'NO'
      },
      'deník': { 
        url: 'https://images.seeklogo.com/logo-png/38/3/denik-cz-logo-png_seeklogo-385009.png',
        fallback: 'DE'
      },
      'denik': { 
        url: 'https://images.seeklogo.com/logo-png/38/3/denik-cz-logo-png_seeklogo-385009.png',
        fallback: 'DE'
      },
      'rozhlas': { 
        url: 'https://www.irozhlas.cz/sites/all/themes/custom/irozhlas/img/logo-mail.png',
        fallback: 'IR'
      },
      'ceskenoviny' : {
        url: 'https://i3.cn.cz/15/1706796525_CTK_logo.jpg',
        fallback: 'CN'
      }
    };

    // Check for exact matches first
    for (const [key, value] of Object.entries(logoMap)) {
      if (lowerSite.includes(key)) {
        return value;
      }
    }

    // Default fallback - try to extract domain and use first letters
    const firstTwoLetters = sourceSite.replace(/[^a-zA-ZčšžýáíéěůúóťďňĚŠČŘŽÝÁÍÉŮÚÓŤĎŇ]/g, '').substring(0, 2).toUpperCase();
    
    return {
      url: `https://logo.clearbit.com/${lowerSite.replace(/\s+/g, '')}.cz`,
      fallback: firstTwoLetters || 'WEB'
    };
  };

  return (
    <div className="space-y-4">
      {inputNews.map((news, index) => {
        const logoData = getSourceLogo(news.source_site);

        return (
          <a
            key={index}
            href={news.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block group"
          >
            <Card className="card-elevated border-border/50 hover:border-primary/30 transition-all relative overflow-hidden">
              {/* Subtle gradient accent on hover */}
              <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

              <CardContent className="pt-6">
                <div className="flex gap-4 items-start">
                  {/* Source logo */}
                  <div className="w-16 h-16 rounded-xl bg-accent/50 border border-border/50 flex items-center justify-center flex-shrink-0 group-hover:scale-110 group-hover:border-primary/20 transition-all duration-300 shadow-sm">
                    <LogoWithFallback
                      logoUrl={logoData.url}
                      sourceSite={news.source_site}
                      fallback={logoData.fallback}
                    />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold mb-3 leading-tight group-hover:text-primary transition-colors">
                      {news.title}
                    </h3>

                    <div className="flex flex-wrap gap-2 mb-3">
                      {news.author && (
                        <Badge variant="secondary" className="gap-1.5 text-xs">
                          <User className="h-3 w-3" />
                          {news.author}
                        </Badge>
                      )}
                      <Badge variant="secondary" className="gap-1.5 text-xs">
                        <Newspaper className="h-3 w-3" />
                        {news.source_site}
                      </Badge>
                      <Badge variant="secondary" className="gap-1.5 text-xs">
                        <Calendar className="h-3 w-3" />
                        {formatDate(news.publication_date)}
                      </Badge>
                    </div>

                    <span className="inline-flex items-center gap-1.5 text-primary font-medium text-sm transition-all group-hover:gap-2">
                      Přečíst původní článek
                      <ExternalLink className="h-3.5 w-3.5" />
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </a>
        );
      })}
    </div>
  );
};

export default InputNewsList;