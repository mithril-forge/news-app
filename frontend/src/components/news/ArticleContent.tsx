/**
 * Component for displaying article content with proper formatting and new design
 * Handles both plain text and HTML content
 */

interface ArticleContentProps {
  /** The content text or HTML of the article */
  content: string;
  /** Whether the content should be rendered as HTML */
  isHtml?: boolean;
}

export default function ArticleContent({ content, isHtml = false }: ArticleContentProps) {
  // Enhanced styles for better typography
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

  // For HTML content, use dangerouslySetInnerHTML (assuming trusted content)
  if (isHtml) {
    return (
      <div className={`prose prose-lg max-w-none ${contentStyles}`}>
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    );
  }
  
  // For plain text, preserve whitespace and add paragraph breaks
  const formattedContent = content
    .split('\n\n')
    .filter(paragraph => paragraph.trim().length > 0)
    .map((paragraph, index) => (
      <p key={index} className="mb-6 text-lg leading-relaxed text-gray-700">
        {paragraph.trim()}
      </p>
    ));
  
  return (
    <div className={`prose prose-lg max-w-none ${contentStyles}`}>
      {formattedContent}
    </div>
  );
}