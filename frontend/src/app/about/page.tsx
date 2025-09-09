/**
 * About page (O nás) - explains the mission and value proposition
 */
import { Suspense } from 'react';
import { fetchTopics } from '@/services/api';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Loading from '@/components/common/Loading';
import { Metadata } from 'next';

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
    <div className="min-h-screen flex flex-col" style={{
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
      <Header
        categories={categories}
        activeCategory=""
      />

      <Suspense fallback={<Loading />}>
        <main className="max-w-4xl mx-auto px-4 py-12 w-full flex-grow">
          <article className="bg-white rounded-3xl shadow-xl overflow-hidden">
            {/* Gradient top border */}
            <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-green-500"></div>

            <div className="p-8 md:p-12">
              {/* Header */}
              <div className="text-center mb-12">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl text-white">🧠</span>
                </div>
                <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
                  O nás
                </h1>
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                  Proč jsme vytvořili Tvůj Novinář a jak chceme změnit způsob, jakým konzumujete zprávy
                </p>
              </div>

              {/* Content sections */}
              <div className="prose prose-lg max-w-none space-y-8">

                {/* Problem section */}
                <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-2xl p-8 border border-red-100">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">⚠️</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800 mb-4">Problém, který řešíme</h2>
                      <p className="text-gray-700 leading-relaxed mb-4">
                        Cítíme se zahlceni množstvím informací v dnešním světě. Každý zpravodajský web přidává do zpráv svůj vlastní úhel pohledu a zaujatost, což ztěžuje získání objektivního přehledu o skutečně důležitých událostech.
                      </p>
                      <p className="text-gray-700 leading-relaxed">
                        Ne každý má čas číst všechny zprávy a ne všechny zprávy jsou pro každého stejně zajímavé nebo relevantní.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Solution section */}
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">💡</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800 mb-4">Naše řešení</h2>
                      <p className="text-gray-700 leading-relaxed mb-4">
                        Proto je zásadní získávat aktualizace z více zdrojů současně. Naše články shrnují veškeré potřebné informace, aniž by vynechaly jakékoli důležité detaily.
                      </p>
                      <p className="text-gray-700 leading-relaxed">
                        Nabízíme způsob, jak získat právě ty zprávy, které tě zajímají, ve stručném a přehledném shrnutí. Není potřeba procházet desítky webů nebo aplikací - vše, co potřebuješ, je na jednom místě.
                      </p>
                    </div>
                  </div>
                </div>

                {/* How it works section */}
                <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-8 border border-green-100">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">⚙️</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800 mb-4">Jak to funguje</h2>
                      <ul className="space-y-3 text-gray-700">
                        <li className="flex items-start space-x-3">
                          <span className="text-blue-500 mt-1">📊</span>
                          <span><strong>Agregace ze všech zdrojů:</strong> Shromažďujeme zprávy ze všech hlavních českých médií</span>
                        </li>
                        <li className="flex items-start space-x-3">
                          <span className="text-blue-500 mt-1">🤖</span>
                          <span><strong>AI analýza:</strong> Inteligentní algoritmy zpracují a shrnou klíčové informace bez zaujatosti</span>
                        </li>
                        <li className="flex items-start space-x-3">
                          <span className="text-blue-500 mt-1">🎯</span>
                          <span><strong>Personalizace:</strong> Získáte pouze zprávy, které odpovídají tvým zájmům</span>
                        </li>
                        <li className="flex items-start space-x-3">
                          <span className="text-blue-500 mt-1">⚡</span>
                          <span><strong>Úspora času:</strong> Stručné a přesné shrnutí místo hodin čtení</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Mission section */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border border-purple-100">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">🎯</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800 mb-4">Naše mise</h2>
                      <p className="text-gray-700 leading-relaxed">
                        Chceme ti vrátit kontrolu nad informacemi, které konzumuješ. Místo toho, abys byl zahlen zprávami, které tě nezajímají, nebo abys zmeškal důležité události, dostaneš přesně to, co potřebuješ vědět - rychle, objektivně a personalizovaně.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Call to action */}
              <div className="text-center mt-12 pt-8 border-t border-gray-200">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Začněte už dnes</h3>
                <p className="text-gray-600 mb-6">
                  Vytvoř si svůj personalizovaný zpravodajský feed a ušetři si čas na věci, které jsou pro tebe skutečně důležité.
                </p>
                <a
                  href="/feed"
                  className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 font-semibold"
                >
                  <span>🚀</span>
                  <span>Vytvořit AI Feed</span>
                </a>
              </div>
            </div>
          </article>
        </main>
      </Suspense>

      <Footer
        categories={categories}
      />
    </div>
  );
}
