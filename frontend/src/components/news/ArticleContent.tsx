/**
 * Component for displaying article content with proper formatting
 * Handles both plain text and HTML content
 */

interface ArticleContentProps {
    /** The content text or HTML of the article */
    content: string;
    /** Whether the content should be rendered as HTML */
    isHtml?: boolean;
  }
  
  export default function ArticleContent({ content, isHtml = false }: ArticleContentProps) {
    // For HTML content, use dangerouslySetInnerHTML (assuming trusted content)
    if (isHtml) {
      return (
        <div 
          className="prose prose-lg max-w-none text-gray-700" 
          dangerouslySetInnerHTML={{ __html: content }} 
        />
      );
    }
    
    // For plain text, preserve whitespace
    return (
      <div className="prose prose-lg max-w-none text-gray-700 whitespace-pre-wrap">
        {content}
      </div>
    );
  }