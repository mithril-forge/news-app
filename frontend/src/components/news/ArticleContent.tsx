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

  // Handle HTML content
  if (contentType === 'html') {
    return (
      <div 
        className={`prose prose-lg max-w-none ${contentStyles} ${className}`}
        dangerouslySetInnerHTML={{ __html: content }} 
      />
    );
  }

  // Handle plain text content
  if (contentType === 'text') {
    const paragraphs = content
      .split(/\n\s*\n/)
      .filter(paragraph => paragraph.trim().length > 0);
    
    return (
      <div className={`prose prose-lg max-w-none ${contentStyles} ${className}`}>
        {paragraphs.map((paragraph, index) => (
          <p key={index} className="mb-6 text-lg leading-relaxed text-gray-700">
            {paragraph.trim()}
          </p>
        ))}
      </div>
    );
  }

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

  // Handle HTML content
  if (contentType === 'html') {
    return (
      <div 
        className={`prose prose-lg max-w-none ${contentStyles} ${className}`}
        dangerouslySetInnerHTML={{ __html: content }} 
      />
    );
  }

  // Handle plain text content
  if (contentType === 'text') {
    const paragraphs = content
      .split(/\n\s*\n/)
      .filter(paragraph => paragraph.trim().length > 0);
    
    return (
      <div className={`prose prose-lg max-w-none ${contentStyles} ${className}`}>
        {paragraphs.map((paragraph, index) => (
          <p key={index} className="mb-6 text-lg leading-relaxed text-gray-700">
            {paragraph.trim()}
          </p>
        ))}
      </div>
    );
  }

  // Handle markdown content with react-markdown (simple approach)
  return (
    <div className={`prose prose-lg max-w-none ${contentStyles} ${className}`}>
      <ReactMarkdown>
        {content}
      </ReactMarkdown>
    </div>
  );

  // Handle markdown content with react-markdown (simple approach)
  return (
    <div className={`prose prose-lg max-w-none ${contentStyles} ${className}`}>
      <ReactMarkdown>
        {content}
      </ReactMarkdown>
    </div>
  );
}