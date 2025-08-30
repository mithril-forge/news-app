// utils/categoryEmojis.ts
export interface CategoryEmoji {
  emoji: string;
  color: string;
  bgColor: string;
}

export const categoryEmojiMap: Record<string, CategoryEmoji> = {
  Politika: {
    emoji: "🏛️",
    color: "#8B5A3C", // hnědá pro institucionální charakter
    bgColor: "linear-gradient(135deg, #8B5A3C20, #A0522D20)",
  },
  Sport: {
    emoji: "⚽",
    color: "#2E8B57", // zelená jako trávník
    bgColor: "linear-gradient(135deg, #2E8B5720, #228B2220)",
  },
  Kultura: {
    emoji: "🎭",
    color: "#8A2BE2", // fialová pro kreativitu
    bgColor: "linear-gradient(135deg, #8A2BE220, #9932CC20)",
  },
  Ekonomika: {
    emoji: "📈",
    color: "#FFD700", // zlatá pro peníze/hodnoty
    bgColor: "linear-gradient(135deg, #FFD70020, #FFA50020)",
  },
  Věda: {
    emoji: "🔬",
    color: "#0066CC", // modrá pro vědu/technologie
    bgColor: "linear-gradient(135deg, #0066CC20, #0052A320)",
  },
  Domácí: {
    emoji: "🏠",
    color: "#D2691E", // oranžová pro domov/teplo
    bgColor: "linear-gradient(135deg, #D2691E20, #CD853F20)",
  },
  Zahraničí: {
    emoji: "🌍",
    color: "#4682B4", // modrá pro svět/oceány
    bgColor: "linear-gradient(135deg, #4682B420, #5F9EA020)",
  },
  Vše: {
    emoji: "📰",
    color: "#708090", // šedá pro neutralitu
    bgColor: "linear-gradient(135deg, #70809020, #77889920)",
  },
  Počasí: {
    emoji: "⛅️",
    color: "#87CEEB", // nebesky modrá
    bgColor: "linear-gradient(135deg, #87CEEB20, #ADD8E620)",
  },
  Společnost: {
    emoji: "👥",
    color: "#E6194B", // červená pro sociální témata
    bgColor: "linear-gradient(135deg, #E6194B20, #DC143C20)",
  },
  Krimi: {
    emoji: "🚨",
    color: "#CC0000", // výrazně červená pro nebezpečí
    bgColor: "linear-gradient(135deg, #CC000020, #B7001F20)",
  },
  Ostatní: {
    emoji: "🔗",
    color: "#696969", // tmavě šedá pro "ostatní"
    bgColor: "linear-gradient(135deg, #69696920, #80808020)",
  }
}

/**
 * Získá emoji informace pro danou kategorii
 * @param categoryName - Název kategorie
 * @returns CategoryEmoji objekt s emoji, barvou a pozadím
 */
export const getCategoryEmoji = (categoryName: string): CategoryEmoji => {
  return categoryEmojiMap[categoryName] || categoryEmojiMap["Vše"];
};
