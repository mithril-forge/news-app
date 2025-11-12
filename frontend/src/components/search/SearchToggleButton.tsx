// components/search/SearchToggleButton.tsx
"use client";

interface SearchToggleButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export default function SearchToggleButton({
  isOpen,
  onClick,
}: SearchToggleButtonProps) {
  return (
    <button
      onClick={onClick}
      className="sm:hidden p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
      aria-label="Hledat"
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        {isOpen ? (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        ) : (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        )}
      </svg>
    </button>
  );
}