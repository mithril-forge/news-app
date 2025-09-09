/**
 * InputNewsList server component for displaying input news sources with new design
 */
import Link from 'next/link';
import LogoWithFallback from '@/components/common/LogoWithFallback';

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
            className="block group cursor-pointer"
          >
            <div className="bg-white rounded-2xl shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden border border-gray-100">
              <div className="p-6">
                <div className="flex gap-4 items-start">
                  {/* Source logo */}
                  <div className="w-16 h-16 rounded-xl bg-blue-50 border-2 border-blue-200 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                    <LogoWithFallback 
                      logoUrl={logoData.url}
                      sourceSite={news.source_site}
                      fallback={logoData.fallback}
                    />
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3 leading-tight group-hover:text-blue-600 transition-colors">
                      {news.title}
                    </h3>
                    
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                      {news.author && (
                        <span className="flex items-center gap-2">
                          <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                          </svg>
                          <span className="font-medium">Autor:</span> 
                          <span>{news.author}</span>
                        </span>
                      )}
                      <span className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2v8h12V6H4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">Zdroj:</span> 
                        <span>{news.source_site}</span>
                      </span>
                      <span className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">Publikováno:</span> 
                        <span>{formatDate(news.publication_date)}</span>
                      </span>
                    </div>
                    
                    <span className="inline-flex items-center gap-2 text-blue-600 group-hover:text-blue-800 font-medium text-sm transition-all group-hover:gap-4">
                      Přečíst původní článek
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                      </svg>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </a>
        );
      })}
    </div>
  );
};

export default InputNewsList;