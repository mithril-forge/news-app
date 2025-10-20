import React from 'react';
import Header from '~/components/layout/Header';
import Footer from '~/components/layout/Footer';

export default function PrivacyPolicyPage() {
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
              Zásady ochrany osobních údajů
            </h1>
            <p className="text-gray-600">
              Platné od: 7. října 2025
            </p>
          </div>

          {/* Content sections */}
          <div className="space-y-10 prose prose-lg max-w-none">

            {/* Section 1 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Správce osobních údajů</h2>
              <p className="text-gray-700"><strong>Název:</strong> Šimon Fouček</p>
              <p className="text-gray-700"><strong>Email:</strong> foucek.simon@gmail.com</p>
            </section>

            {/* Section 2 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Jaké osobní údaje zpracováváme</h2>
              <p className="text-gray-700 mb-3">Při přihlášení k odběru newsletteru od vás shromažďujeme:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Emailová adresa</strong> – pro zasílání newsletteru</li>
              </ul>
            </section>

            {/* Section 3 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Účel zpracování</h2>
              <p className="text-gray-700 mb-3">Vaši emailovou adresu zpracováváme výhradně za účelem:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Zasílání našeho newsletteru s novinkami, tipy a nabídkami</li>
                <li>Komunikace související s obsahem newsletteru</li>
              </ul>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Právní základ zpracování</h2>
              <p className="text-gray-700 mb-3">Zpracování vašeho emailu je založeno na:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Vašem souhlasu podle čl. 6 odst. 1 písm. a) GDPR</li>
                <li>Souhlas udělujete aktivním zaškrtnutím políčka při registraci</li>
              </ul>
            </section>

            {/* Section 5 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Jak dlouho údaje uchováváme</h2>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Vaši emailovou adresu uchováváme po dobu vašeho souhlasu</li>
                <li>Po odhlášení z newsletteru váš email okamžitě smažeme (max. do 30 dnů)</li>
                <li>Evidenci o udělení souhlasu uchováváme 3 roky (pro případné právní spory)</li>
              </ul>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Kdo má přístup k vašim údajům</h2>
              <p className="text-gray-700 mb-3">Vaše data můžeme sdílet s těmito zpracovateli:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Poskytovatel emailových služeb</strong> (např. Brevo) – pro technické zajištění rozesílky</li>
                <li><strong>Hosting provider</strong> – pro uložení databáze</li>
              </ul>
              <p className="text-gray-600 text-sm mt-4 italic">
                Všichni zpracovatelé jsou vázáni smlouvou o zpracování a dodržují GDPR.
              </p>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Vaše práva</h2>
              <p className="text-gray-700 mb-3">Máte právo:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Přístup</strong> – zjistit, jaké údaje o vás máme</li>
                <li><strong>Opravu</strong> – opravit nesprávné údaje</li>
                <li><strong>Výmaz</strong> ("právo být zapomenut") – požádat o smazání údajů</li>
                <li><strong>Přenositelnost</strong> – získat své údaje ve strojově čitelném formátu</li>
                <li><strong>Odvolání souhlasu</strong> – kdykoliv odhlásit newsletter (odkaz v každém emailu)</li>
                <li><strong>Podat stížnost</strong> u Úřadu pro ochranu osobních údajů (uoou.cz)</li>
              </ul>
              <p className="text-gray-700 mt-4">
                Pro uplatnění práv nás kontaktujte na: <a href="mailto:support@tvujnovinar.cz" className="text-blue-600 hover:underline font-semibold">support@tvujnovinar.cz</a>
              </p>
            </section>

            {/* Section 8 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Zabezpečení údajů</h2>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Používáme šifrované spojení (HTTPS/TLS)</li>
                <li>Přístup k databázi mají pouze oprávněné osoby</li>
                <li>Pravidelně provádíme zálohy a bezpečnostní audit</li>
              </ul>
            </section>

            {/* Section 9 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Cookies a sledování</h2>
              <p className="text-gray-700 mb-3">Na našich webových stránkách používáme cookies pro:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong>Nezbytné cookies</strong> – zajištění funkčnosti webu (nevyžadují souhlas)</li>
                <li><strong>Analytické cookies</strong> – měření návštěvnosti (Google Analytics) – vyžadují souhlas</li>
                <li><strong>Reklamní cookies</strong> – personalizované reklamy (Google AdSense) – vyžadují souhlas</li>
              </ul>
              <p className="text-gray-600 text-sm mt-4 italic">
                Své preference cookies můžete kdykoliv změnit v [Nastavení cookies].
              </p>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Změny těchto zásad</h2>
              <p className="text-gray-700">
                Tyto zásady můžeme aktualizovat. O významných změnách vás budeme informovat emailem nebo na webu.
              </p>
            </section>

            {/* Section 11 */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Kontakt</h2>
              <p className="text-gray-700">
                V případě dotazů nás kontaktujte:<br />
                <a href="mailto:support@tvujnovinar.cz" className="text-blue-600 hover:underline font-semibold text-lg">support@tvujnovinar.cz</a>
              </p>
            </section>
          </div>

          {/* Footer note */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-gray-500 text-sm text-center">
              Tyto zásady ochrany osobních údajů jsou v souladu s Nařízením Evropského parlamentu a Rady (EU) 2016/679 (GDPR)
            </p>
          </div>
        </article>
      </main>

      <Footer categories={categories}></Footer>
    </div>
  );
}