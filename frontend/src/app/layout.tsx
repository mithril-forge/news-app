/**
 * Root layout component that wraps all pages
 * Provides global styles and metadata
 */
import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";
import "@/styles/globals.css";

// Define site metadata
export const metadata: Metadata = {
  title: "Tvůj Novinář | Tvoje denní dávka novinek",
  description: "Tvůj spolehlivý zdroj nejnovějších zpráv z České republiky i ze světa.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

// Configure Geist font
const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="cs" className={`${geist.variable}`}>
      <head>
        {/* Cookiebot - FIRST! */}
        <Script
          id="Cookiebot"
          src="https://consent.cookiebot.com/uc.js"
          data-cbid="VÁŠE-COOKIEBOT-ID"
          data-blockingmode="auto"
          strategy="beforeInteractive"
        />

        {/* Google Consent Mode V2 */}
        <Script id="google-consent-mode" strategy="beforeInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('consent', 'default', {
              'ad_storage': 'denied',
              'ad_user_data': 'denied',
              'ad_personalization': 'denied',
              'analytics_storage': 'denied'
            });
          `}
        </Script>

        {/* Google AdSense */}
        <Script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-VÁŠE-PUBLISHER-ID"
          crossOrigin="anonymous"
          strategy="afterInteractive"
        />
      </head>

      <body>{children}</body>
    </html>
  );
}