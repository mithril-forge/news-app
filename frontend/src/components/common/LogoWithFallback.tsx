'use client';

import { useState } from 'react';

interface LogoWithFallbackProps {
  logoUrl: string;
  sourceSite: string;
  fallback: string;
}

const LogoWithFallback = ({ logoUrl, sourceSite, fallback }: LogoWithFallbackProps) => {
  const [hasError, setHasError] = useState(false);
  
  if (hasError) {
    return (
      <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center text-blue-700 text-sm font-bold shadow-sm">
        {fallback}
      </div>
    );
  }
  
  return (
    <img 
      src={logoUrl} 
      alt={`${sourceSite} logo`}
      className="w-10 h-10 object-contain rounded-lg"
      onError={() => setHasError(true)}
      onLoad={(e) => {
        // Check if image is actually loaded (not a placeholder)
        const img = e.target as HTMLImageElement;
        if (img.naturalWidth === 0 || img.naturalHeight === 0) {
          setHasError(true);
        }
      }}
    />
  );
};

export default LogoWithFallback;