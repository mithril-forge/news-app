/**
 * Utility functions for date formatting and manipulation
 */

/**
 * Format date string to localized date string
 * @param dateString - ISO date string
 * @param locale - Locale string (defaults to Czech)
 * @returns Formatted date string
 */
export function formatDate(dateString: string, locale = 'cs-CZ'): string {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateString; // Return original string if parsing fails
    }
  }
  
  /**
   * Format date to relative time (e.g. "2 hours ago")
   * @param dateString - ISO date string
   * @param locale - Locale string (defaults to Czech)
   * @returns Relative time string
   */
  export function formatRelativeTime(dateString: string, locale = 'cs-CZ'): string {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffMinutes < 60) {
        return `${diffMinutes} ${pluralizeCzech(diffMinutes, 'minuta', 'minuty', 'minut')}`;
      } else if (diffHours < 24) {
        return `${diffHours} ${pluralizeCzech(diffHours, 'hodina', 'hodiny', 'hodin')}`;
      } else if (diffDays < 7) {
        return `${diffDays} ${pluralizeCzech(diffDays, 'den', 'dny', 'dní')}`;
      } else {
        return formatDate(dateString, locale);
      }
    } catch (error) {
      console.error('Error formatting relative date:', error);
      return dateString;
    }
  }
  
  /**
   * Helper function for Czech plural forms
   */
  function pluralizeCzech(count: number, form1: string, form2to4: string, form5plus: string): string {
    if (count === 1) {
      return form1;
    } else if (count >= 2 && count <= 4) {
      return form2to4;
    } else {
      return form5plus;
    }
  }