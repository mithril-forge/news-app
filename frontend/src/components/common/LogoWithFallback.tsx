'use client';

import { useState } from 'react';
import Image from 'next/image';

interface LogoWithFallbackProps {
  logoUrl: string;
  sourceSite: string;
  fallback: string;
}

const LogoWithFallback = ({ logoUrl, sourceSite, fallback }: LogoWithFallbackProps) => {
  const [hasError, setHasError] = useState(false);

  if (hasError || !logoUrl) {
    return (
      <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center text-blue-700 text-sm font-bold shadow-sm">
        {fallback}
      </div>
    );
  }

  return (
    <Image
      src={logoUrl}
      alt={`${sourceSite} logo`}
      width={40}
      height={40}
      className="object-contain rounded-lg"
      onError={() => setHasError(true)}
      unoptimized={false}
    />
  );
};

export default LogoWithFallback;
