// utils/categoryEmojis.ts
export interface CategoryEmoji {
  emoji: string;
  color: string;
  bgColor: string;
}

export const categoryEmojiMap: Record<string, CategoryEmoji> = {
  'Politika': { 
    emoji: '🏛️', 
    color: '#667eea', 
    bgColor: 'linear-gradient(135deg, #667eea20, #764ba220)' 
  },
  'Sport': { 
    emoji: '⚽', 
    color: '#f093fb', 
    bgColor: 'linear-gradient(135deg, #f093fb20, #f5576c20)' 
  },
  'Technologie': { 
    emoji: '💻', 
    color: '#4facfe', 
    bgColor: 'linear-gradient(135deg, #4facfe20, #00f2fe20)' 
  },
  'Kultura': { 
    emoji: '🎭', 
    color: '#43e97b', 
    bgColor: 'linear-gradient(135deg, #43e97b20, #38f9d720)' 
  },
  'Ekonomika': { 
    emoji: '📈', 
    color: '#fa709a', 
    bgColor: 'linear-gradient(135deg, #fa709a20, #fee14020)' 
  },
  'Věda': { 
    emoji: '🔬', 
    color: '#667eea', 
    bgColor: 'linear-gradient(135deg, #667eea20, #764ba220)' 
  },
  'Zdraví': { 
    emoji: '🏥', 
    color: '#27ae60', 
    bgColor: 'linear-gradient(135deg, #27ae6020, #2ecc7120)' 
  },
  'Domácí': { 
    emoji: '🏠', 
    color: '#e67e22', 
    bgColor: 'linear-gradient(135deg, #e67e2220, #d35400020)' 
  },
  'Zahraničí': { 
    emoji: '🌍', 
    color: '#3498db', 
    bgColor: 'linear-gradient(135deg, #3498db20, #2980b920)' 
  },
  'Vše': { 
    emoji: '📰', 
    color: '#e74c3c', 
    bgColor: 'linear-gradient(135deg, #e74c3c20, #c0392b20)' 
  }
};

/**
 * Získá emoji informace pro danou kategorii
 * @param categoryName - Název kategorie
 * @returns CategoryEmoji objekt s emoji, barvou a pozadím
 */
export const getCategoryEmoji = (categoryName: string): CategoryEmoji => {
  return categoryEmojiMap[categoryName] || categoryEmojiMap['Vše'];
};