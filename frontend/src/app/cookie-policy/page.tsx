import React from 'react';
import Footer from '~/components/layout/Footer';
import Header from '~/components/layout/Header';

export default function CookiePolicyPage() {
    const categories = ["AI Feed", "Vše"];
    
  return (
        <div className="min-h-screen flex flex-col" style={{
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
            <Header
              categories={categories}
              activeCategory=""
            />

      <main className="max-w-4xl mx-auto px-4 py-12">
        <article className="bg-white rounded-lg shadow-sm p-8 md:p-12">
          {/* Header */}
          <div className="mb-12 pb-8 border-b border-gray-200">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">
              Zásady používání cookies
            </h1>
            <p className="text-gray-600">
              Platné od: 7. října 2025
            </p>
          </div>

          {/* Content sections */}
          <div className="space-y-10 prose prose-lg max-w-none">

            {/* What are cookies */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Co jsou cookies?</h2>
              <p className="text-gray-700">
                Cookies jsou malé textové soubory, které se ukládají do vašeho zařízení (počítač, telefon, tablet) při návštěvě webových stránek. Umožňují webu zapamatovat si vaše akce a preference.
              </p>
            </section>

            {/* Types of cookies */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Jaké cookies používáme?</h2>

              {/* Necessary cookies */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">1. Nezbytné cookies (Strictly Necessary)</h3>
                <p className="text-gray-700 mb-4">
                  Tyto cookies jsou nutné pro základní funkčnost webu a nevyžadují váš souhlas.
                </p>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-300">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Název</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Účel</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Platnost</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Poskytovatel</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">cookieconsent</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Uložení vašich cookie preferencí</td>
                        <td className="px-4 py-3 text-sm text-gray-700">12 měsíců</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Náš web</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Analytics cookies */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">2. Analytické cookies (Analytics)</h3>
                <p className="text-gray-700 mb-4">
                  Pomáhají nám pochopit, jak návštěvníci používají web. Vyžadují váš souhlas.
                </p>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-300">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Název</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Účel</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Platnost</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Poskytovatel</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">_ga</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Rozlišení uživatelů</td>
                        <td className="px-4 py-3 text-sm text-gray-700">2 roky</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google Analytics</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">_gid</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Rozlišení uživatelů</td>
                        <td className="px-4 py-3 text-sm text-gray-700">24 hodin</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google Analytics</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm text-gray-700">_gat</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Omezení rychlosti požadavků</td>
                        <td className="px-4 py-3 text-sm text-gray-700">1 minuta</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google Analytics</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-700 mb-1"><strong>Zpracovatel:</strong> Google Ireland Limited</p>
                  <p className="text-sm text-gray-700 mb-1"><strong>Přenos do třetích zemí:</strong> USA (na základě standardních smluvních doložek)</p>
                  <p className="text-sm text-gray-700">
                    <strong>Více info:</strong> <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">policies.google.com/privacy</a>
                  </p>
                </div>
              </div>

              {/* Marketing cookies */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">3. Reklamní cookies (Marketing/Advertising)</h3>
                <p className="text-gray-700 mb-4">
                  Používají se k zobrazování relevantních reklam. Vyžadují váš souhlas.
                </p>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-300">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Název</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Účel</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Platnost</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">Poskytovatel</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">IDE</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Personalizované reklamy</td>
                        <td className="px-4 py-3 text-sm text-gray-700">13 měsíců</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google (DoubleClick)</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">test_cookie</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Kontrola podpory cookies</td>
                        <td className="px-4 py-3 text-sm text-gray-700">15 minut</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google (DoubleClick)</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-700">__gads</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Měření interakcí s reklamami</td>
                        <td className="px-4 py-3 text-sm text-gray-700">13 měsíců</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google AdSense</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm text-gray-700">__gac</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Informace o reklamních kampaních</td>
                        <td className="px-4 py-3 text-sm text-gray-700">90 dní</td>
                        <td className="px-4 py-3 text-sm text-gray-700">Google AdSense</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-700 mb-1"><strong>Zpracovatel:</strong> Google Ireland Limited</p>
                  <p className="text-sm text-gray-700 mb-1"><strong>Přenos do třetích zemí:</strong> USA (na základě standardních smluvních doložek)</p>
                  <p className="text-sm text-gray-700">
                    <strong>Více info:</strong> <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">policies.google.com/technologies/ads</a>
                  </p>
                </div>
              </div>
            </section>

            {/* Managing cookies */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Jak spravovat cookies?</h2>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Prostřednictvím našeho webu</h3>
              <p className="text-gray-700 mb-4">
                Své preference můžete kdykoliv změnit kliknutím na Nastavení cookies ve spodní části obrazovky.
              </p>
 

              <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Prostřednictvím prohlížeče</h3>
              <p className="text-gray-700 mb-3">
                Můžete také nastavit svůj prohlížeč tak, aby cookies blokoval nebo vás upozorňoval před jejich uložením:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Chrome:</strong> Nastavení → Soukromí a zabezpečení → Cookies</li>
                <li><strong>Firefox:</strong> Nastavení → Soukromí a zabezpečení</li>
                <li><strong>Safari:</strong> Předvolby → Soukromí</li>
                <li><strong>Edge:</strong> Nastavení → Soukromí, vyhledávání a služby</li>
              </ul>
              <p className="text-gray-600 italic mt-4">
                ⚠️ Pozor: Zablokování cookies může omezit funkčnost webu.
              </p>
            </section>

            {/* Third party cookies */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Cookies třetích stran</h2>
              <p className="text-gray-700 mb-3">
                Některé cookies na našem webu pocházejí od externích služeb:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Google Analytics</strong> – měření návštěvnosti</li>
                <li><strong>Google AdSense</strong> – zobrazování reklam</li>
              </ul>
              <p className="text-gray-700 mt-4">
                Tyto služby mohou cookies využívat k vlastním účelům. Doporučujeme přečíst jejich zásady ochrany soukromí.
              </p>
            </section>

            {/* Your rights */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Vaše práva</h2>
              <p className="text-gray-700 mb-3">Máte právo:</p>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✅</span>
                  <span>Kdykoli změnit své cookie preference</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✅</span>
                  <span>Odmítnout analytické a reklamní cookies</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✅</span>
                  <span>Smazat cookies ve svém prohlížeči</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✅</span>
                  <span>Získat více informací o zpracování</span>
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Kontakt</h2>
              <p className="text-gray-700 mb-3">Máte-li dotazy k cookies, kontaktujte nás:</p>
              <ul className="space-y-2 text-gray-700">
                <li><strong>Email:</strong> <a href="mailto:support@tvujnovinar.cz" className="text-blue-600 hover:underline">support@tvujnovinar.cz</a></li>
                <li><strong>Správce:</strong> Šimon Fouček</li>
              </ul>
            </section>

            <section>
              <p className="text-gray-600 text-sm">
                <strong>Poslední aktualizace:</strong> 7. října 2025
              </p>
            </section>

            <section className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <p className="text-gray-700">
                Více informací o zpracování osobních údajů najdete v našich{' '}
                <a href="/terms" className="text-blue-600 hover:underline font-semibold">
                  Zásadách ochrany osobních údajů
                </a>.
              </p>
            </section>
          </div>
        </article>
      </main>

      <Footer 
        categories={categories} 
      />
    </div>
  );
}