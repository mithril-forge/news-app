/**
 * About page (O nás) - explains the mission and value proposition
 */
import { Suspense } from 'react';
import { fetchTopics } from '@/services/api';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Loading from '@/components/common/Loading';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Separator } from '~/components/ui/separator';
import { AlertCircle, Lightbulb, Cog, Target, Rocket } from 'lucide-react';
import { Metadata } from 'next';
import Link from 'next/link';

// Configure ISR revalidation
export const revalidate = 3600; // Revalidate every hour

export const metadata: Metadata = {
  title: 'O nás | Tvůj Novinář',
  description: 'Proč jsme vytvořili Tvůj Novinář - náš přístup k překonání informačního přetížení pomocí AI.',
};

export default async function AboutPage() {
  // Fetch data for header with fallback during build
  let topicsData = [];
  try {
    topicsData = await fetchTopics();
  } catch (error) {
    console.warn('Failed to fetch topics for about page (likely during build), using fallback:', error);
    // Fallback topics for build time
    topicsData = [
      { name: 'Politika', id: 1 },
      { name: 'Sport', id: 2 },
      { name: 'Kultura', id: 3 },
      { name: 'Ekonomika', id: 4 },
      { name: 'Věda', id: 5 }
    ];
  }
  const categories = ["AI Feed", "Vše", ...topicsData.map(topic => topic.name)];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header
        categories={categories}
        activeCategory=""
      />

      <Suspense fallback={<Loading />}>
        <main className="max-w-4xl mx-auto px-4 py-12 w-full flex-grow">
          <Card className="card-elevated overflow-hidden relative">
            {/* Subtle gradient background pattern */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 pointer-events-none" />

            {/* Page header */}
            <CardHeader className="text-center pb-8 pt-12 relative">
              <div className="w-24 h-24 ai-gradient rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary/30 animate-pulse">
                <span className="text-5xl">🧠</span>
              </div>
              <CardTitle className="text-4xl md:text-5xl mb-4 bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text">
                O nás
              </CardTitle>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Proč jsme vytvořili Tvůj Novinář a jak chceme změnit způsob, jakým konzumujete zprávy
              </p>
            </CardHeader>

            <CardContent className="space-y-6 pb-12 relative">
              {/* Problem section */}
              <Card className="card-elevated border-2 border-destructive/30 bg-destructive/5 overflow-hidden relative">
                <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-destructive/80 via-destructive/40 to-transparent" />
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-destructive/20 to-destructive/10 rounded-xl flex items-center justify-center flex-shrink-0 border-2 border-destructive/30 shadow-md">
                      <AlertCircle className="h-7 w-7 text-destructive" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-4">Problém, který řešíme</CardTitle>
                      <div className="space-y-3 text-muted-foreground">
                        <p className="leading-relaxed">
                          Cítíme se zahlceni množstvím informací v dnešním světě. Každý zpravodajský web přidává do zpráv svůj vlastní úhel pohledu a zaujatost, což ztěžuje získání objektivního přehledu o skutečně důležitých událostech.
                        </p>
                        <p className="leading-relaxed">
                          Ne každý má čas číst všechny zprávy a ne všechny zprávy jsou pro každého stejně zajímavé nebo relevantní.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Solution section */}
              <Card className="card-elevated ai-gradient-border overflow-hidden relative">
                <div className="absolute inset-x-0 top-0 h-1 ai-gradient" />
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 ai-gradient rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/30">
                      <Lightbulb className="h-7 w-7 text-white" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-4">Naše řešení</CardTitle>
                      <div className="space-y-3 text-muted-foreground">
                        <p className="leading-relaxed">
                          Proto je zásadní získávat aktualizace z více zdrojů současně. Naše články shrnují veškeré potřebné informace, aniž by vynechaly jakékoli důležité detaily.
                        </p>
                        <p className="leading-relaxed">
                          Nabízíme způsob, jak získat právě ty zprávy, které tě zajímají, ve stručném a přehledném shrnutí. Není potřeba procházet desítky webů nebo aplikací - vše, co potřebuješ, je na jednom místě.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* How it works section */}
              <Card className="border-accent/30 bg-accent/5">
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-accent/20 rounded-xl flex items-center justify-center flex-shrink-0 border border-accent/30">
                      <Cog className="h-6 w-6 text-accent-foreground" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-4">Jak to funguje</CardTitle>
                      <ul className="space-y-4 text-muted-foreground">
                        <li className="flex items-start gap-3">
                          <span className="text-primary font-semibold">📊</span>
                          <span><strong className="text-foreground">Agregace ze všech zdrojů:</strong> Shromažďujeme zprávy ze všech hlavních českých médií</span>
                        </li>
                        <li className="flex items-start gap-3">
                          <span className="text-primary font-semibold">🤖</span>
                          <span><strong className="text-foreground">AI analýza:</strong> Inteligentní algoritmy zpracují a shrnou klíčové informace bez zaujatosti</span>
                        </li>
                        <li className="flex items-start gap-3">
                          <span className="text-primary font-semibold">🎯</span>
                          <span><strong className="text-foreground">Personalizace:</strong> Získáte pouze zprávy, které odpovídají tvým zájmům</span>
                        </li>
                        <li className="flex items-start gap-3">
                          <span className="text-primary font-semibold">⚡</span>
                          <span><strong className="text-foreground">Úspora času:</strong> Stručné a přesné shrnutí místo hodin čtení</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Mission section */}
              <Card className="border-secondary/30 bg-secondary/20">
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center flex-shrink-0 border border-secondary-foreground/10">
                      <Target className="h-6 w-6 text-secondary-foreground" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-4">Naše mise</CardTitle>
                      <p className="text-muted-foreground leading-relaxed">
                        Chceme ti vrátit kontrolu nad informacemi, které konzumuješ. Místo toho, abys byl zahlen zprávami, které tě nezajímají, nebo abys zmeškal důležité události, dostaneš přesně to, co potřebuješ vědět - rychle, objektivně a personalizovaně.
                      </p>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              <Separator className="my-8" />

              {/* Call to action */}
              <div className="text-center pt-8">
                <h3 className="text-3xl font-bold mb-4 text-gradient">Začněte už dnes</h3>
                <p className="text-muted-foreground mb-8 text-lg max-w-xl mx-auto">
                  Vytvoř si svůj personalizovaný zpravodajský feed a ušetři si čas na věci, které jsou pro tebe skutečně důležité.
                </p>
                <Button asChild size="lg" className="ai-gradient gap-2 text-lg px-8 py-6 shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 transition-all">
                  <Link href="/feed">
                    <Rocket className="h-5 w-5" />
                    Vytvořit AI Feed
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </main>
      </Suspense>

      <Footer
        categories={categories}
      />
    </div>
  );
}
