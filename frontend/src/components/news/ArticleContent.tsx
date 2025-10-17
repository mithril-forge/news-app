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

  // Enhanced styles using design tokens
  const contentStyles = `
    prose-headings:text-foreground
    prose-headings:font-bold
    prose-h1:text-3xl
    prose-h2:text-2xl
    prose-h3:text-xl
    prose-p:text-foreground/90
    prose-p:leading-relaxed
    prose-p:mb-6
    prose-a:text-primary
    prose-a:hover:text-primary/80
    prose-a:transition-colors
    prose-strong:text-foreground
    prose-em:text-muted-foreground
    prose-blockquote:border-l-4
    prose-blockquote:border-primary/60
    prose-blockquote:pl-6
    prose-blockquote:italic
    prose-blockquote:bg-accent/50
    prose-blockquote:py-4
    prose-blockquote:rounded-r-xl
    prose-ul:list-disc
    prose-ol:list-decimal
    prose-li:mb-2
    prose-code:bg-accent
    prose-code:text-foreground
    prose-code:px-2
    prose-code:py-1
    prose-code:rounded-md
    prose-code:text-sm
    prose-code:border
    prose-code:border-border
  `;

  return (
    <div className={`prose prose-lg max-w-none dark:prose-invert ${contentStyles} ${className}`}>
      <ReactMarkdown components={{
          // Custom component styling with design tokens
          h1: ({children}) => (
            <h1 className="text-3xl font-bold text-foreground mb-8 mt-12 tracking-tight">
              {children}
            </h1>
          ),
          h2: ({children}) => (
            <h2 className="text-2xl font-bold text-foreground mb-6 mt-10 tracking-tight">
              {children}
            </h2>
          ),
          h3: ({children}) => (
            <h3 className="text-xl font-bold text-foreground mb-4 mt-8 tracking-tight">
              {children}
            </h3>
          ),
          h4: ({children}) => (
            <h4 className="text-lg font-bold text-foreground mb-4 mt-6 tracking-tight">
              {children}
            </h4>
          ),
          p: ({children}) => (
            <p className="mb-6 text-lg leading-relaxed text-foreground/90">
              {children}
            </p>
          ),
          a: ({href, children}) => (
            <a
              href={href}
              className="text-primary hover:text-primary/80 underline underline-offset-2 transition-colors font-medium"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          strong: ({children}) => (
            <strong className="text-foreground font-semibold">
              {children}
            </strong>
          ),
          em: ({children}) => (
            <em className="text-muted-foreground">
              {children}
            </em>
          ),
          code: ({children}) => (
            <code className="bg-accent text-foreground px-2 py-1 rounded-md text-sm border border-border">
              {children}
            </code>
          ),
          blockquote: ({children}) => (
            <blockquote className="border-l-4 border-primary/60 pl-6 italic bg-accent/50 py-4 rounded-r-xl my-6 relative overflow-hidden">
              <div className="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-primary via-primary/60 to-transparent" />
              {children}
            </blockquote>
          ),
          ul: ({children}) => (
            <ul className="list-disc pl-6 space-y-2 my-6">
              {children}
            </ul>
          ),
          ol: ({children}) => (
            <ol className="list-decimal pl-6 space-y-2 my-6">
              {children}
            </ol>
          ),
          li: ({children}) => (
            <li className="text-foreground/90 leading-relaxed">
              {children}
            </li>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}