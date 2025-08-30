import ReactMarkdown from 'react-markdown';

interface ArticleContentProps {
  /** The content text, HTML, or markdown of the article */
  content: string;
  /** Content type: 'text', 'html', or 'markdown' */
  contentType?: 'text' | 'html' | 'markdown';
  /** Additional CSS classes */
  className?: string;
}

export default function ArticleContent({ 
  content, 
  contentType = 'markdown',
  className = '' 
}: ArticleContentProps) {

  // Enhanced styles for better typography (your original styling)
  const contentStyles = `
    prose-headings:text-gray-800 
    prose-headings:font-bold 
    prose-h1:text-3xl 
    prose-h2:text-2xl 
    prose-h3:text-xl 
    prose-p:text-gray-700 
    prose-p:leading-relaxed 
    prose-p:mb-6 
    prose-a:text-blue-600 
    prose-a:hover:text-blue-800 
    prose-strong:text-gray-800 
    prose-em:text-gray-600
    prose-blockquote:border-l-4 
    prose-blockquote:border-blue-500 
    prose-blockquote:pl-6 
    prose-blockquote:italic 
    prose-blockquote:bg-blue-50 
    prose-blockquote:py-4 
    prose-blockquote:rounded-r-lg
    prose-ul:list-disc 
    prose-ol:list-decimal 
    prose-li:mb-2
    prose-code:bg-gray-100 
    prose-code:px-2 
    prose-code:py-1 
    prose-code:rounded 
    prose-code:text-sm
  `;

  return (
    <div className={`prose prose-lg max-w-none ${contentStyles} ${className}`}>
      <  ReactMarkdown     components={{
          // Custom component styling
          h1: ({children}) => <h1 className="text-3xl font-bold text-gray-800 mb-8 mt-12">{children}</h1>,
          h2: ({children}) => <h2 className="text-2xl font-bold text-gray-800 mb-6 mt-10">{children}</h2>,
          h3: ({children}) => <h3 className="text-xl font-bold text-gray-800 mb-4 mt-8">{children}</h3>,
          h4: ({children}) => <h4 className="text-l font-bold text-gray-800 mb-4 mt-6">{children}</h4>,
        p: ({children}) => <p className="mb-6 text-lg leading-relaxed text-gray-700">{children}</p>,
          a: ({href, children}) => (
            <a href={href} className="text-blue-600 hover:text-blue-800">
              {children}
            </a>
          ),
          strong: ({children}) => <strong className="text-gray-800">{children}</strong>,
          em: ({children}) => <em className="text-gray-600">{children}</em>,
          code: ({children}) => (
            <code className="bg-gray-100 px-2 py-1 rounded text-sm">
              {children}
            </code>
          ),
          blockquote: ({children}) => (
            <blockquote className="border-l-4 border-blue-500 pl-6 italic bg-blue-50 py-4 rounded-r-lg">
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}