/**
 * Core type definitions for the application
 */

/**
 * Topic/category model
 */
export interface Topic {
    id: string;
    name: string;
  }
  
  /**
   * Tag model for article classification
   */
  export interface Tag {
    id: string;
    text: string;
  }
  
  /**
   * News article model
   */
  export interface NewsArticle {
    id: string;
    title: string;
    summary: string;
    image_url: string | null;
    updated_at: string;
    created_at: string;
    topic: Topic;
    tags: Tag[];
    date?: string; // Formatted date for display
    isHtml?: boolean; // Whether content is HTML formatted
  }

    /**
   * Detailed article model
   */
  export interface NewsDetailed extends NewsArticle {
    content: string;
  }