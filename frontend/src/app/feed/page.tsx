"use client";

import { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ArticleCard from "@/components/news/ArticleCard";
import {
  fetchTopics,
  getAccountDetails,
  setAIPrompt,
  getAllLatestPick,
  getPickNews,
} from "@/services/api";
import {
  deleteAccount,
  generatePick,
  linkAnonymousPickToUser,
} from "@/services/api/feed";
import { NewsArticle, Topic } from "@/types";

// Storage keys
const EMAIL_KEY = "news_app_user_email";
const PROMPT_KEY = "news_app_user_prompt";
const ANONYMOUS_PICK_HASH_KEY = "news_app_anonymous_pick_hash";
const ANONYMOUS_PICK_DATE_KEY = "news_app_anonymous_pick_date";

type FeedbackType = "success" | "error" | "info" | "warning" | null;

interface FeedbackMessage {
  type: FeedbackType;
  message: string;
}

// Email capture modal component
const EmailModal = ({
  isOpen,
  onClose,
  onSubmit,
  onLogin,
  loading,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (email: string) => Promise<{ success: boolean; error?: string }>;
  onLogin: (email: string) => Promise<{ success: boolean; error?: string }>;
  loading: boolean;
}) => {
  const [email, setEmail] = useState("");
  const [modalFeedback, setModalFeedback] = useState<string | null>(null);
  const [isLoginMode, setIsLoginMode] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check terms acceptance only for registration, not login
    if (!isLoginMode && !termsAccepted) {
      setModalFeedback("Musíte souhlasit se zásadami ochrany osobních údajů");
      return;
    }
    
    if (email.trim()) {
      setModalFeedback(null);
      const result = isLoginMode
        ? await onLogin(email.trim())
        : await onSubmit(email.trim());
      if (!result.success && result.error) {
        setModalFeedback(result.error);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 cursor-pointer text-xl text-gray-400 hover:text-gray-600"
        >
          ×
        </button>

        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-green-500 to-blue-600">
            <span className="text-2xl text-white">
              {isLoginMode ? "🔐" : "🎉"}
            </span>
          </div>
          <h2 className="mb-2 text-2xl font-bold text-gray-800">
            {isLoginMode
              ? "Přihlásit se do účtu"
              : "Skvělé! Tvůj personalizovaný feed je připraven"}
          </h2>
          <p className="text-gray-600">
            {isLoginMode
              ? "Zadejte emailovou adresu spojenou s tvým účtem"
              : "Chcete si uložit svůj prompt pro příští návštěvy? Stačí zadat email a už se o nic nemusíte starat."}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="vas@email.cz"
              required
            />
          </div>

          {/* Terms acceptance checkbox - only for registration */}
          {!isLoginMode && (
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="terms"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <label htmlFor="terms" className="text-sm text-gray-700">
                Souhlasím se{" "}
                <a
                  href="/terms"
                  target="_blank"
                  className="text-blue-600 underline hover:text-blue-800"
                >
                  zásadami ochrany osobních údajů
                </a>
              </label>
            </div>
          )}

          {/* Modal feedback */}
          {modalFeedback && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3">
              <p className="text-sm font-medium text-red-800">
                {modalFeedback}
              </p>
            </div>
          )}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 cursor-pointer rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold text-white transition-all hover:from-blue-700 hover:to-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-white"></div>
                  <span>{isLoginMode ? "Přihlašuji..." : "Ukládám..."}</span>
                </div>
              ) : isLoginMode ? (
                "🚀 Přihlásit se"
              ) : (
                "💾 Uložit a pokračovat"
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="cursor-pointer rounded-xl border border-gray-300 px-6 py-3 text-gray-700 transition-colors hover:bg-gray-50"
            >
              {isLoginMode ? "Zrušit" : "Možná později"}
            </button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <p className="mb-2 text-sm text-gray-600">
            {isLoginMode ? "Nemáte ještě účet?" : "Už máte účet?"}
          </p>
          <button
            type="button"
            onClick={() => {
              setIsLoginMode(!isLoginMode);
              setModalFeedback(null);
              setEmail("");
              setTermsAccepted(false);
            }}
            className="cursor-pointer font-medium text-blue-600 underline hover:text-blue-800"
          >
            {isLoginMode
              ? "Vytvořte si nový"
              : "Přihlásit se do existujícího účtu"}
          </button>
        </div>
      </div>
    </div>
  );
};

// Feedback component
const FeedbackComponent = ({ feedback }: { feedback: FeedbackMessage }) => {
  const bgColor =
    feedback.type === "success"
      ? "bg-green-50 border-green-200"
      : feedback.type === "error"
        ? "bg-red-50 border-red-200"
        : feedback.type === "warning"
          ? "bg-yellow-50 border-yellow-200"
          : "bg-blue-50 border-blue-200";
  const textColor =
    feedback.type === "success"
      ? "text-green-800"
      : feedback.type === "error"
        ? "text-red-800"
        : feedback.type === "warning"
          ? "text-yellow-800"
          : "text-blue-800";

  return (
    <div className={`${bgColor} mb-6 rounded-lg border p-4`}>
      <p className={`${textColor} font-medium`}>{feedback.message}</p>
    </div>
  );
};

// Loading component for pick generation
const LoadingPickGeneration = ({
  pickGenerationStep,
}: {
  pickGenerationStep: string;
}) => (
  <div className="py-8 text-center">
    <div className="inline-flex items-center space-x-3 rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4">
      <div className="h-6 w-6 animate-spin rounded-full border-b-2 border-blue-600"></div>
      <div>
        <p className="font-medium text-blue-800">
          Vytvářím tvůj personalizovaný feed...
        </p>
        <p className="text-sm text-blue-600">{pickGenerationStep}</p>
      </div>
    </div>
  </div>
);

export default function PersonalFeedPage() {
  const [email, setEmail] = useState("");
  const [prompt, setPrompt] = useState("");
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null);
  const [isGeneratingPick, setIsGeneratingPick] = useState(false);
  const [pickGenerationStep, setPickGenerationStep] = useState("");
  const [showPromptForm, setShowPromptForm] = useState(true);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [isEditingPrompt, setIsEditingPrompt] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState("");
  const [originalPrompt, setOriginalPrompt] = useState("");

  useEffect(() => {
    const savedEmail = localStorage.getItem(EMAIL_KEY);
    const savedPrompt = localStorage.getItem(PROMPT_KEY);
    const savedPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);
    const savedPickDate = localStorage.getItem(ANONYMOUS_PICK_DATE_KEY);

    if (savedEmail) {
      setEmail(savedEmail);
      setIsLoggedIn(true);
      setShowPromptForm(false);
      loadUserData(savedEmail);
    } else if (savedPrompt) {
      setPrompt(savedPrompt);
      setShowPromptForm(false);

      const today = new Date().toDateString();
      if (savedPickHash && savedPickDate === today) {
        loadAnonymousPickByHash(savedPickHash);
      }
    }

    fetchTopics().then(setTopics);
  }, []);

  const loadUserData = async (userEmail: string) => {
    setLoading(true);
    try {
      const accountDetails = await getAccountDetails(userEmail);

      if (accountDetails) {
        setPrompt(accountDetails.prompt || "");

        if (accountDetails.prompt) {
          try {
            const pickResponse = await getAllLatestPick(userEmail);
            setNews(pickResponse.articles);
            setOriginalPrompt(
              pickResponse.description || accountDetails.prompt,
            );

            if (pickResponse.articles.length === 0) {
              setFeedback({
                type: "warning",
                message:
                  "⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus být více obecný.",
              });
            }
          } catch (error) {
            setNews([]);
          }
        }
      }
    } catch (error) {
      console.error("Error loading user data:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadAnonymousPickByHash = async (pickHash: string) => {
    setLoading(true);
    try {
      const pickResponse = await getPickNews(pickHash);
      setNews(pickResponse.articles);
      setOriginalPrompt(pickResponse.description);

      if (pickResponse.articles.length === 0) {
        setFeedback({
          type: "warning",
          message:
            "⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus to příště jinak.",
        });
      }
    } catch (error) {
      console.error("Error loading anonymous pick:", error);
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const generatePickWithFeedback = async (
    userPrompt: string,
    userEmail?: string,
  ) => {
    setIsGeneratingPick(true);
    setPickGenerationStep("Generuji tvůj personalizovaný výběr...");

    try {
      if (userEmail) {
        await generatePick({ userEmail });
        setPickGenerationStep("Načítám tvé články...");
        await loadUserData(userEmail);
      } else {
        const response = await generatePick({ prompt: userPrompt });
        setPickGenerationStep("Načítám tvé články...");
        const pickResponse = await getPickNews(response.hash);
        setNews(pickResponse.articles);
        setOriginalPrompt(pickResponse.description);

        const today = new Date().toDateString();
        localStorage.setItem(ANONYMOUS_PICK_HASH_KEY, response.hash);
        localStorage.setItem(ANONYMOUS_PICK_DATE_KEY, today);

        if (pickResponse.articles.length === 0) {
          setFeedback({
            type: "warning",
            message:
              "⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus to příště jinak.",
          });
          return;
        }
      }

      if (!userEmail) {
        setShowEmailModal(true);
      }

      setFeedback({
        type: "success",
        message:
          "🎉 Tvůj AI personalizovaný feed je připraven! Články byly vybrány přesně podle tvých zájmů.",
      });
    } catch (error) {
      console.error("Error generating pick:", error);
      const errorMessage =
        error instanceof Error ? error.message : String(error);

      if (
        errorMessage.includes("daily limit") ||
        errorMessage.includes("IP blocked") ||
        errorMessage.includes("429")
      ) {
        if (email && isLoggedIn) {
          setFeedback({
            type: "info",
            message:
              "ℹ️ Tvůj prompt byl úspěšně aktualizován! Nové personalizované články budeš dostávat od zítřka.",
          });
        } else {
          setFeedback({
            type: "warning",
            message:
              "⏰ Dosáhl jsi denního limitu generování. Vytvoř si účet nebo zkus zítra.",
          });
        }
      } else if (
        errorMessage.includes("No news items match your interests") ||
        errorMessage.includes("No news available")
      ) {
        setFeedback({
          type: "warning",
          message:
            "⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkuste být více obecný.",
        });
      } else {
        setFeedback({
          type: "error",
          message:
            "❌ Nastala chyba při generování. Zkus to prosím znovu za chvíli.",
        });
      }
    } finally {
      setIsGeneratingPick(false);
      setPickGenerationStep("");
      setShowPromptForm(false);
    }
  };

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    localStorage.setItem(PROMPT_KEY, prompt);
    await generatePickWithFeedback(prompt, isLoggedIn ? email : undefined);
  };

  const handleEmailSubmit = async (
    emailInput: string,
  ): Promise<{ success: boolean; error?: string }> => {
    setSaving(true);
    try {
      const existingAccount = await getAccountDetails(emailInput);
      if (existingAccount) {
        return {
          success: false,
          error: "❌ Účet s touto emailovou adresou již existuje.",
        };
      }

      const anonymousPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);
      await setAIPrompt(emailInput, prompt);

      const hasAnonymousPick = anonymousPickHash && news.length > 0;
      if (hasAnonymousPick) {
        try {
          await linkAnonymousPickToUser(emailInput, anonymousPickHash);
        } catch (error) {
          console.warn("Failed to link anonymous pick to user:", error);
        }
      }

      localStorage.setItem(EMAIL_KEY, emailInput);
      setEmail(emailInput);
      setIsLoggedIn(true);

      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      if (!hasAnonymousPick) {
        await loadUserData(emailInput);
      }

      setShowEmailModal(false);
      setFeedback({
        type: "success",
        message:
          "✅ Tvůj účet byl vytvořen! Prompt je uložen pro příští návštěvy.",
      });

      return { success: true };
    } catch (error) {
      console.error("Error saving email:", error);
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      if (
        errorMessage.includes("already exists") ||
        errorMessage.includes("duplicate")
      ) {
        try {
          localStorage.setItem(EMAIL_KEY, emailInput);
          setEmail(emailInput);
          setIsLoggedIn(true);

          localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
          localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

          await loadUserData(emailInput);

          setShowEmailModal(false);
          setFeedback({
            type: "success",
            message: "✅ Přihlášeni! Našli jsme tvůj existující účet.",
          });

          return { success: true };
        } catch (loginError) {
          return {
            success: false,
            error: "Nastala chyba při přihlašování. Zkus to prosím znovu.",
          };
        }
      } else {
        return {
          success: false,
          error: "Nastala chyba při ukládání. Zkus to prosím znovu.",
        };
      }
    } finally {
      setSaving(false);
    }
  };

  const handleEditPrompt = () => {
    setIsEditingPrompt(true);
    setEditedPrompt(prompt);
  };

  const handleSavePrompt = async () => {
    if (!editedPrompt.trim()) return;

    setSaving(true);
    try {
      await setAIPrompt(email, editedPrompt);
      setPrompt(editedPrompt);
      setIsEditingPrompt(false);

      await generatePickWithFeedback(editedPrompt, email);
    } catch (error) {
      console.error("Error saving prompt:", error);
      setFeedback({
        type: "error",
        message: "❌ Nastala chyba při ukládání. Zkus to prosím znovu.",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditingPrompt(false);
    setEditedPrompt("");
  };

  const handleDeleteAccount = async () => {
    if (!confirm("Opravdu chcete smazat svůj účet? Tato akce je nevratná.")) {
      return;
    }

    setSaving(true);
    try {
      // Call the API to delete the account
      await deleteAccount(email);

      // Clear local storage
      localStorage.removeItem(EMAIL_KEY);
      localStorage.removeItem(PROMPT_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      // Reset state
      setEmail("");
      setPrompt("");
      setNews([]);
      setIsLoggedIn(false);
      setShowPromptForm(true);

      setFeedback({
        type: "success",
        message: "✅ Tvůj účet byl úspěšně smazán.",
      });
    } catch (error) {
      console.error("Error deleting account:", error);
      setFeedback({
        type: "error",
        message: "❌ Nastala chyba při mazání účtu. Zkus to prosím znovu.",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleLogin = async (loginEmail: string) => {
    setSaving(true);
    try {
      const accountDetails = await getAccountDetails(loginEmail);

      if (!accountDetails) {
        setFeedback({
          type: "error",
          message: "❌ Účet s touto emailovou adresou neexistuje.",
        });
        return;
      }

      localStorage.setItem(EMAIL_KEY, loginEmail);
      setEmail(loginEmail);
      setIsLoggedIn(true);
      setShowLoginForm(false);
      setShowPromptForm(false);

      await loadUserData(loginEmail);

      setFeedback({
        type: "success",
        message: "✅ Úspěšně přihlášeni! Vítejte zpět.",
      });
    } catch (error) {
      console.error("Error logging in:", error);
      setFeedback({
        type: "error",
        message: "❌ Nastala chyba při přihlašování. Zkus to prosím znovu.",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleModalLogin = async (
    loginEmail: string,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const accountDetails = await getAccountDetails(loginEmail);

      if (!accountDetails) {
        return {
          success: false,
          error: "❌ Účet s touto emailovou adresou neexistuje.",
        };
      }

      localStorage.setItem(EMAIL_KEY, loginEmail);
      setEmail(loginEmail);
      setIsLoggedIn(true);

      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      await loadUserData(loginEmail);

      setShowEmailModal(false);
      setFeedback({
        type: "success",
        message: "✅ Úspěšně přihlášeni! Vítejte zpět.",
      });

      return { success: true };
    } catch (error) {
      console.error("Error logging in:", error);
      return {
        success: false,
        error: "❌ Nastala chyba při přihlašování. Zkus to prosím znovu.",
      };
    }
  };

  const categories = ["AI Feed", "Vše", ...topics.map((topic) => topic.name)];

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Header categories={categories} activeCategory="AI Feed" />

      <main className="mx-auto w-full max-w-5xl flex-grow px-4 py-8">
        {showPromptForm && !isLoggedIn && (
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex items-center space-x-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white">
                <span className="text-2xl">🧠</span>
              </div>
              <h1 className="text-4xl font-bold text-white">
                Tvoje denní dávka novinek!
              </h1>
            </div>
            <p className="mx-auto max-w-2xl text-lg text-blue-100">
              Náš chytrý novinář vybere jenom ty zprávy, které tě opravdu
              zajímají. Napiš mu jaké zprávy bys chtěl dostávat.
            </p>
          </div>
        )}

        <div className="mb-8 rounded-3xl bg-white p-8 shadow-2xl">
          {feedback && <FeedbackComponent feedback={feedback} />}

          {isGeneratingPick && (
            <LoadingPickGeneration pickGenerationStep={pickGenerationStep} />
          )}

          {showLoginForm ? (
            <div className="rounded-2xl border border-green-200 bg-gradient-to-br from-green-50 to-blue-50 p-8">
              <div className="mb-8 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-r from-green-500 to-blue-600">
                  <span className="text-2xl text-white">🔐</span>
                </div>
                <h2 className="mb-3 text-2xl font-bold text-gray-800">
                  Přihlásit se do účtu
                </h2>
                <p className="text-lg text-gray-600">
                  Zadejte emailovou adresu spojenou s tvým účtem
                </p>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const loginEmail = formData.get("loginEmail") as string;
                  if (loginEmail?.trim()) {
                    handleLogin(loginEmail.trim());
                  }
                }}
                className="space-y-6"
              >
                <div>
                  <label
                    htmlFor="loginEmail"
                    className="mb-3 block text-lg font-semibold text-gray-800"
                  >
                    📧 Emailová adresa
                  </label>
                  <input
                    type="email"
                    id="loginEmail"
                    name="loginEmail"
                    className="w-full rounded-xl border-2 border-gray-200 px-4 py-4 text-lg focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="vas@email.cz"
                    required
                  />
                </div>

                <div className="flex flex-col gap-3 pt-4 sm:flex-row">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex-1 transform cursor-pointer rounded-xl bg-gradient-to-r from-green-600 to-blue-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 hover:from-green-700 hover:to-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saving ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="h-5 w-5 animate-spin rounded-full border-b-2 border-white"></div>
                        <span>Přihlašuji...</span>
                      </div>
                    ) : (
                      <span>🚀 Přihlásit se</span>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowLoginForm(false);
                      setShowPromptForm(true);
                    }}
                    className="cursor-pointer rounded-xl border-2 border-gray-300 px-8 py-4 font-medium text-gray-700 transition-colors hover:bg-gray-50"
                  >
                    Zpět
                  </button>
                </div>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Nemáte ještě účet?{" "}
                  <button
                    onClick={() => {
                      setShowLoginForm(false);
                      setShowPromptForm(true);
                    }}
                    className="cursor-pointer font-medium text-blue-600 hover:text-blue-800"
                  >
                    Vytvořte si nový
                  </button>
                </p>
              </div>
            </div>
          ) : showPromptForm ? (
            <div className="rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50 p-8">
              <div className="mb-8 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600">
                  <span className="text-2xl text-white">✨</span>
                </div>
                <h2 className="mb-3 text-2xl font-bold text-gray-800">
                  {isLoggedIn ? "Upravte své preference" : "Co tě zajímá?"}
                </h2>
                <p className="text-lg text-gray-600">
                  Popiš v přirozeném jazyce, co tě zajímá. AI bude vybírat jen
                  ty články, které jsou pro tebe relevantní.
                </p>
              </div>

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

      <EmailModal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        onSubmit={handleEmailSubmit}
        onLogin={handleModalLogin}
        loading={saving}
      />

      <Footer categories={categories} />
    </div>
  );
}