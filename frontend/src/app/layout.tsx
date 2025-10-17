/**
 * Root layout component that wraps all pages
 * Provides global styles and metadata
 */
import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Toaster } from "~/components/ui/sonner";
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
      <body>
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
