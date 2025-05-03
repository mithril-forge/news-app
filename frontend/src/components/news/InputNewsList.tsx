/**
 * InputNewsList component for displaying input news sources
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

  return (
    <div className="space-y-4">
      {inputNews.map((news, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">
                {news.title}
              </h3>
              <p className="text-sm text-gray-500 mb-2">
                {news.author && (
                  <span className="mr-2">
                    <span className="font-medium">Autor:</span> {news.author}
                  </span>
                )}
                <span className="mr-2">
                  <span className="font-medium">Zdroj:</span> {news.source_site}
                </span>
                <span>
                  <span className="font-medium">Publikováno:</span> {formatDate(news.publication_date)}
                </span>
              </p>
            </div>
            <a 
              href={news.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-shrink-0 bg-blue-100 text-blue-700 hover:bg-blue-200 text-xs font-medium px-3 py-1.5 rounded transition-colors"
            >
              Přečíst
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default InputNewsList;