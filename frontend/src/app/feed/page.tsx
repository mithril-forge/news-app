"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { executeAccountDeletion } from "@/services/api/feed";

// Storage keys (same as in PersonalFeedPage)
const EMAIL_KEY = "news_app_user_email";
const PROMPT_KEY = "news_app_user_prompt";
const ANONYMOUS_PICK_HASH_KEY = "news_app_anonymous_pick_hash";
const ANONYMOUS_PICK_DATE_KEY = "news_app_anonymous_pick_date";

export default function DeleteAccountPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const categories = ["AI Feed", "Vše"];

  useEffect(() => {
    const executeDelete = async () => {
      if (!token) {
        setStatus("error");
        setMessage("Neplatný odkaz - chybí token.");
        return;
      }
      
      try {
        // Call the API function
        await executeAccountDeletion(token);
        
        // Clear all localStorage on successful deletion
        localStorage.removeItem(EMAIL_KEY);
        localStorage.removeItem(PROMPT_KEY);
        localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
        localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);
        
        setStatus("success");
        setMessage("Váš účet byl úspěšně smazán.");
        
      } catch (error) {
        setStatus("error");
        setMessage(error instanceof Error ? error.message : "Chyba při mazání účtu");
      }
    };

    executeDelete();
  }, [token]);

  return (
    <div className="flex min-h-screen flex-col" style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
      <Header categories={categories} activeCategory="" />

      <main className="mx-auto w-full max-w-5xl flex-grow px-4 py-8">
        <div className="rounded-3xl bg-white p-8 shadow-2xl">
          {status === "loading" && (
            <div className="text-center py-12">
              <div className="inline-flex items-center space-x-3 rounded-2xl border border-blue-200 bg-blue-50 px-6 py-4">
                <div className="h-6 w-6 animate-spin rounded-full border-b-2 border-blue-600"></div>
                <span className="font-medium text-blue-800">Mažu váš účet...</span>
              </div>
            </div>
          )}

          {status === "success" && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">✅</div>
              <h1 className="text-3xl font-bold text-green-600 mb-4">Účet byl smazán</h1>
              <p className="text-lg text-gray-600 mb-8">{message}</p>
              <a href="/" className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-8 rounded-xl transition-all">
                Přejít na hlavní stránku
              </a>
            </div>
          )}
              <form onSubmit={handlePromptSubmit} className="space-y-6">
                <div>
                  <label
                    htmlFor="prompt"
                    className="mb-3 block text-lg font-semibold text-gray-800"
                  >
                    💭 Co tě zajímá?
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={5}
                    className="w-full resize-none rounded-xl border-2 border-gray-200 px-4 py-4 text-lg focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="Například: Chci mít přehled o politických událostech v ČR a jenom ty nejdůležitější celosvětové zprávy z oblasti technologií a byznysu."

                    required
                  />
                  <div className="mt-3 flex items-start space-x-2">
                    <span className="text-blue-500">💡</span>
                    <p className="text-sm text-gray-600">
                      <strong>Tip:</strong> Buďte konkrétní! Můžete zadat témata, regiony, typy zpráv nebo dokonce tón článků, který preferujete. Měj ale na paměti, že naše články pokrývají hlavně ty nejdůležitější události z ČR a světa. Na naší stránce tak například nenajdeš různé lokální události z tvého okolí.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-3 pt-4 sm:flex-row">
                  <button
                    type="submit"
                    disabled={saving || isGeneratingPick}
                    className="flex-1 transform cursor-pointer rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 hover:from-blue-700 hover:to-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saving || isGeneratingPick ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="h-5 w-5 animate-spin rounded-full border-b-2 border-white"></div>
                        <span>{saving ? "Ukládám..." : "Vytvářím..."}</span>
                      </div>
                    ) : (
                      <span>
                        🚀{" "}
                        {isLoggedIn
                          ? "Aktualizovat AI Feed"
                          : "Vytvořit AI Feed"}
                      </span>
                    )}
                  </button>
                  {isLoggedIn && (
                    <button
                      type="button"
                      onClick={() => setShowPromptForm(false)}
                      className="cursor-pointer rounded-xl border-2 border-gray-300 px-8 py-4 font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      Zrušit
                    </button>
                  )}
                </div>

                {!isLoggedIn && (
                  <div className="mt-6 text-center">
                    <p className="mb-2 text-sm text-gray-600">Už máte účet?</p>
                    <button
                      type="button"
                      onClick={() => {
                        setShowPromptForm(false);
                        setShowLoginForm(true);
                      }}
                      className="cursor-pointer font-medium text-blue-600 underline hover:text-blue-800"
                    >
                      Přihlásit se do existujícího účtu
                    </button>
                  </div>
                )}
              </form>
            </div>
          ) : (
            <div className="space-y-8">
              {!isLoggedIn && prompt && (
                <div className="flex items-center justify-between rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-blue-600">👤</span>
                    <span className="font-medium text-gray-700">
                      Anonymní uživatel
                    </span>
                    <span className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800">
                      Dočasný účet
                    </span>
                  </div>
                  <button
                    onClick={() => setShowEmailModal(true)}
                    className="transform cursor-pointer rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:scale-105 hover:from-blue-700 hover:to-purple-700"
                  >
                    💾 Vytvořit účet
                  </button>
                </div>
              )}

              {prompt && (
                <div className="rounded-2xl border border-green-200 bg-gradient-to-br from-green-50 to-blue-50 p-8">
                  <div className="mb-6 flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-green-500 to-blue-600">
                        <span className="text-xl text-white">🎯</span>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-800">
                          Tvá perzonalizovaná preference
                        </h3>
                        <div className="flex items-center space-x-2">
                          <p className="text-gray-600">
                            {isLoggedIn
                              ? "Podle toho AI vybírá tvé články"
                              : "AI vybralo články podle tohoto promptu"}
                          </p>
                          {isLoggedIn && email && (
                            <>
                              <span className="text-gray-400">•</span>
                              <span className="text-sm text-gray-500">
                                {email}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    {isLoggedIn && (
                      <div className="flex gap-2">
                        <button
                          onClick={handleEditPrompt}
                          className="flex cursor-pointer items-center space-x-2 rounded-xl border-2 border-gray-300 bg-white px-4 py-2 text-gray-700 transition-all hover:border-blue-400 hover:text-blue-600 hover:shadow-md"
                        >
                          <span>✏️</span>
                          <span className="font-medium">Upravit</span>
                        </button>
                        <button
                          onClick={handleDeleteAccount}
                          className="flex cursor-pointer items-center space-x-2 rounded-xl border-2 border-red-300 bg-white px-4 py-2 text-red-600 transition-all hover:border-red-500 hover:bg-red-50 hover:shadow-md"
                        >
                          <span>🗑️</span>
                          <span className="font-medium">Smazat</span>
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="rounded-xl border border-gray-200 bg-white p-6">
                    {isEditingPrompt ? (
                      <div className="space-y-4">
                        <div className="flex items-start space-x-3">
                          <span className="mt-1 text-xl text-blue-500">✏️</span>
                          <div className="flex-1">
                            <textarea
                              value={editedPrompt}
                              onChange={(e) => setEditedPrompt(e.target.value)}
                              rows={4}
                              className="w-full resize-none rounded-xl border-2 border-gray-200 px-4 py-3 text-lg focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
                              placeholder="Popiš, co tě zajímá..."
                            />
                          </div>
                        </div>
                        <div className="flex items-center justify-end space-x-3">
                          <button
                            onClick={handleCancelEdit}
                            className="cursor-pointer rounded-lg border border-gray-300 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50"
                          >
                            Zrušit
                          </button>
                          <button
                            onClick={handleSavePrompt}
                            disabled={saving || !editedPrompt.trim()}
                            className="cursor-pointer rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-2 font-semibold text-white transition-all hover:from-blue-700 hover:to-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {saving ? "Ukládám..." : "Uložit"}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start space-x-3">
                        <span className="text-xl text-green-500">💭</span>
                        <div className="flex-1">
                          <p className="text-lg leading-relaxed text-gray-800">
                            {prompt}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {loading ? (
                <div className="py-12 text-center">
                  <div className="inline-flex items-center space-x-3 rounded-2xl border border-blue-200 bg-blue-50 px-6 py-4">
                    <div className="h-6 w-6 animate-spin rounded-full border-b-2 border-blue-600"></div>
                    <span className="font-medium text-blue-800">
                      Načítám tvé články...
                    </span>
                  </div>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                    <div className="flex items-center space-x-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-green-500 to-blue-600">
                        <span className="text-white">📰</span>
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-gray-800">
                          Tvůj AI výběr
                        </h2>
                        <p className="text-gray-600">
                          {news.length > 0
                            ? `${news.length} ${news.length === 1 ? "nejnovější článek" : news.length >= 2 && news.length <= 4 ? "nejnovější články" : "nejnovějších článků"} podle tvých preferencí`
                            : "Žádné články nebyly nalezeny pro tvůj prompt"}
                        </p>
                        {originalPrompt && (
                          <p className="mt-1 text-sm text-gray-500">
                            Téma výběru: {originalPrompt}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {news.length > 0 && (
                    <div className="grid gap-8">
                      {news.map((article) => (
                        <ArticleCard key={article.id} article={article} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <Footer categories={categories} />
    </div>
  );
}