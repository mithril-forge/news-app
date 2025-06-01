/**
 * InputNewsList component for displaying input news sources with new design
 */
import Link from 'next/link';

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

  // Get emoji for source site (simple mapping)
  const getSourceEmoji = (sourceSite: string): string => {
    const lowerSite = sourceSite.toLowerCase();
    if (lowerSite.includes('čt24') || lowerSite.includes('ct24')) return '📺';
    if (lowerSite.includes('idnes')) return '📰';
    if (lowerSite.includes('aktuálně') || lowerSite.includes('aktualne')) return '🗞️';
    if (lowerSite.includes('novinky')) return '📋';
    if (lowerSite.includes('blesk')) return '⚡';
    if (lowerSite.includes('denik')) return '📖';
    if (lowerSite.includes('ihned')) return '⏰';
    if (lowerSite.includes('forum24')) return '🗣️';
    if (lowerSite.includes('reflex')) return '🔍';
    return '🌐'; // Default emoji for unknown sources
  };

  return (
    <div className="space-y-4">
      {inputNews.map((news, index) => (
        <div 
          key={index} 
          className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100"
        >
          <div className="p-6">
            <div className="flex gap-4 items-start">
              {/* Source emoji */}
              <div className="w-12 h-12 rounded-xl bg-blue-50 border-2 border-blue-200 flex items-center justify-center text-xl flex-shrink-0">
                {getSourceEmoji(news.source_site)}
              </div>
              
              {/* Content */}
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 leading-tight">
                  {news.title}
                </h3>
                
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                  {news.author && (
                    <span className="flex items-center gap-1">
                      <span className="font-medium">👤 Autor:</span> 
                      <span>{news.author}</span>
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <span className="font-medium">🏢 Zdroj:</span> 
                    <span>{news.source_site}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-medium">📅 Publikováno:</span> 
                    <span>{formatDate(news.publication_date)}</span>
                  </span>
                </div>
                
                <a 
                  href={news.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 bg-blue-600 text-white hover:bg-blue-700 text-sm font-medium px-4 py-2 rounded-xl transition-all hover:scale-105 hover:shadow-md"
                >
                  Přečíst zdroj
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default InputNewsList;