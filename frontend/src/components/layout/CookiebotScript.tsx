'use client';

import { useEffect } from 'react';

export default function CookiebotScript() {
  useEffect(() => {
    // Load Cookiebot
    const cookiebotScript = document.createElement('script');
    cookiebotScript.id = 'Cookiebot';
    cookiebotScript.src = 'https://consent.cookiebot.com/uc.js';
    cookiebotScript.setAttribute('data-cbid', 'VÁŠE-COOKIEBOT-ID');
    cookiebotScript.setAttribute('data-blockingmode', 'auto');
    cookiebotScript.type = 'text/javascript';
    document.body.appendChild(cookiebotScript);

    // Load Google AdSense
    const adsenseScript = document.createElement('script');
    adsenseScript.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-VÁŠE-PUBLISHER-ID';
    adsenseScript.async = true;
    adsenseScript.crossOrigin = 'anonymous';
    document.body.appendChild(adsenseScript);

    return () => {
      // Cleanup on unmount
      if (cookiebotScript.parentNode) {
        cookiebotScript.parentNode.removeChild(cookiebotScript);
      }
      if (adsenseScript.parentNode) {
        adsenseScript.parentNode.removeChild(adsenseScript);
      }
    };
  }, []);

  return null;
}