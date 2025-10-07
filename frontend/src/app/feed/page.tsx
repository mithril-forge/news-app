'use client'

import { useState, useEffect } from 'react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Loading from '@/components/common/Loading';
import ArticleCard from '@/components/news/ArticleCard';
import { fetchTopics, getAccountDetails, setAIPrompt, getAllLatestPick, getPickNews } from '@/services/api';
import { generatePick, linkAnonymousPickToUser, type NewsPickResponse } from '@/services/api/feed';
import type { PickGenerationResponse } from '@/services/api/feed';
import { NewsArticle, Topic } from '@/types';

// Storage keys
const EMAIL_KEY = 'news_app_user_email';
const PROMPT_KEY = 'news_app_user_prompt';
const DAILY_GENERATION_KEY = 'news_app_daily_generation';
const ANONYMOUS_PICK_HASH_KEY = 'news_app_anonymous_pick_hash';
const ANONYMOUS_PICK_DATE_KEY = 'news_app_anonymous_pick_date';

type FeedbackType = 'success' | 'error' | 'info' | 'warning' | null;

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
  loading
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (email: string) => Promise<{ success: boolean; error?: string }>;
  onLogin: (email: string) => Promise<{ success: boolean; error?: string }>;
  loading: boolean;
}) => {
  const [email, setEmail] = useState('');
  const [modalFeedback, setModalFeedback] = useState<string | null>(null);
  const [isLoginMode, setIsLoginMode] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl cursor-pointer"
        >
          ×
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl text-white">{isLoginMode ? '🔐' : '🎉'}</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {isLoginMode ? 'Přihlásit se do účtu' : 'Skvělé! Tvůj personalizovaný feed je připraven'}
          </h2>
          <p className="text-gray-600">
            {isLoginMode
              ? 'Zadejte emailovou adresu spojenou s tvým účtem'
              : 'Chcete si uložit svůj prompt pro příští návštěvy? Stačí zadat email a už se o nic nemusíte starat.'
            }
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="vas@email.cz"
              required
            />
          </div>

          {/* Modal feedback */}
          {modalFeedback && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm font-medium">{modalFeedback}</p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 font-semibold cursor-pointer disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>{isLoginMode ? 'Přihlašuji...' : 'Ukládám...'}</span>
                </div>
              ) : (
                isLoginMode ? '🚀 Přihlásit se' : '💾 Uložit a pokračovat'
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors text-gray-700 cursor-pointer"
            >
              {isLoginMode ? 'Zrušit' : 'Možná později'}
            </button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm mb-2">
            {isLoginMode ? 'Nemáte ještě účet?' : 'Už máte účet?'}
          </p>
          <button
            type="button"
            onClick={() => {
              setIsLoginMode(!isLoginMode);
              setModalFeedback(null); // Clear any error messages when switching
              setEmail(''); // Clear email field
            }}
            className="text-blue-600 hover:text-blue-800 font-medium cursor-pointer underline"
          >
            {isLoginMode ? 'Vytvořte si nový' : 'Přihlásit se do existujícího účtu'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Feedback component
const FeedbackComponent = ({ feedback }: { feedback: FeedbackMessage }) => {
  const bgColor = feedback.type === 'success' ? 'bg-green-50 border-green-200' :
                 feedback.type === 'error' ? 'bg-red-50 border-red-200' :
                 feedback.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                 'bg-blue-50 border-blue-200';
  const textColor = feedback.type === 'success' ? 'text-green-800' :
                   feedback.type === 'error' ? 'text-red-800' :
                   feedback.type === 'warning' ? 'text-yellow-800' :
                   'text-blue-800';

  return (
    <div className={`${bgColor} border rounded-lg p-4 mb-6`}>
      <p className={`${textColor} font-medium`}>{feedback.message}</p>
    </div>
  );
};

// Loading component for pick generation
const LoadingPickGeneration = ({ pickGenerationStep }: { pickGenerationStep: string }) => (
  <div className="text-center py-8">
    <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 rounded-2xl border border-blue-200">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <div>
        <p className="text-blue-800 font-medium">Vytvářím tvůj personalizovaný feed...</p>
        <p className="text-blue-600 text-sm">{pickGenerationStep}</p>
      </div>
    </div>
  </div>
);

export default function PersonalFeedPage() {
  const [email, setEmail] = useState('');
  const [prompt, setPrompt] = useState('');
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null);
  const [isGeneratingPick, setIsGeneratingPick] = useState(false);
  const [pickGenerationStep, setPickGenerationStep] = useState('');
  const [showPromptForm, setShowPromptForm] = useState(true);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [isEditingPrompt, setIsEditingPrompt] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState('');
  const [originalPrompt, setOriginalPrompt] = useState('');

  // Load saved data from localStorage on mount
  useEffect(() => {
    const savedEmail = localStorage.getItem(EMAIL_KEY);
    const savedPrompt = localStorage.getItem(PROMPT_KEY);
    const savedPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);
    const savedPickDate = localStorage.getItem(ANONYMOUS_PICK_DATE_KEY);

    if (savedEmail) {
      // Logged in user
      setEmail(savedEmail);
      setIsLoggedIn(true);
      setShowPromptForm(false);
      loadUserData(savedEmail);
    } else if (savedPrompt) {
      // Anonymous user
      setPrompt(savedPrompt);
      setShowPromptForm(false);

      // Check if we have saved pick from today
      const today = new Date().toDateString();
      if (savedPickHash && savedPickDate === today) {
        // Load articles from backend using the hash
        loadAnonymousPickByHash(savedPickHash);
      }
    }


    // Load topics for header
    fetchTopics().then(setTopics);
  }, []);

  const loadUserData = async (userEmail: string) => {
    setLoading(true);
    try {
      const accountDetails = await getAccountDetails(userEmail);

      if (accountDetails) {
        setPrompt(accountDetails.prompt || '');

        // Try to get all articles from their latest pick
        if (accountDetails.prompt) {
          try {
            const pickResponse = await getAllLatestPick(userEmail);
            setNews(pickResponse.articles);
            setOriginalPrompt(pickResponse.description || accountDetails.prompt);

            // Show warning if no articles found
            if (pickResponse.articles.length === 0) {
              setFeedback({
                type: 'warning',
                message: '⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus být více obecný.'
              });
            }
          } catch (error) {
            setNews([]);
          }
        }
      }
    } catch (error) {
      console.error('Error loading user data:', error);
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

      // Show warning if no articles found
      if (pickResponse.articles.length === 0) {
        setFeedback({
          type: 'warning',
          message: '⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus to příště jinak.'
        });
      }
    } catch (error) {
      console.error('Error loading anonymous pick:', error);
      // Clear invalid hash
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const generatePickWithFeedback = async (userPrompt: string, userEmail?: string) => {

    setIsGeneratingPick(true);
    setPickGenerationStep('Generuji tvůj personalizovaný výběr...');

    try {
      // Generate pick
      if (userEmail) {
        // Logged in user
        await generatePick({ userEmail });
        setPickGenerationStep('Načítám tvé články...');
        await loadUserData(userEmail);
      } else {
        // Anonymous user
        const response = await generatePick({ prompt: userPrompt });
        setPickGenerationStep('Načítám tvé články...');
        const pickResponse = await getPickNews(response.hash);
        setNews(pickResponse.articles);
        setOriginalPrompt(pickResponse.description);

        // Save pick hash to localStorage for persistence
        const today = new Date().toDateString();
        localStorage.setItem(ANONYMOUS_PICK_HASH_KEY, response.hash);
        localStorage.setItem(ANONYMOUS_PICK_DATE_KEY, today);

        // Show warning if no articles found
        if (pickResponse.articles.length === 0) {
          setFeedback({
            type: 'warning',
            message: '⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkus to příště jinak.'
          });
          return; // Don't show success message
        }
      }

      // Show success and email modal for anonymous users
      if (!userEmail) {
        setShowEmailModal(true);
      }

      setFeedback({
        type: 'success',
        message: '🎉 Tvůj AI personalizovaný feed je připraven! Články byly vybrány přesně podle tvých zájmů.'
      });

    } catch (error) {
      console.error('Error generating pick:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);

      if (errorMessage.includes('daily limit') || errorMessage.includes('IP blocked') || errorMessage.includes('429')) {
        // Check if this was triggered from a prompt update by a logged-in user
        if (email && isLoggedIn) {
          setFeedback({
            type: 'info',
            message: 'ℹ️ Tvůj prompt byl úspěšně aktualizován! Nové personalizované články budeš dostávat od zítřka.'
          });
        } else {
          setFeedback({
            type: 'warning',
            message: '⏰ Dosáhl jsi denního limitu generování. Vytvoř si účet nebo zkus zítra.'
          });
        }
      } else if (errorMessage.includes('No news items match your interests') || errorMessage.includes('No news available')) {
        setFeedback({
          type: 'warning',
          message: '⚠️ Tvůj prompt byl příliš unikátní a nenašli jsme žádné odpovídající články. Zkuste být více obecný.'
        });
      } else {
        setFeedback({
          type: 'error',
          message: '❌ Nastala chyba při generování. Zkus to prosím znovu za chvíli.'
        });
      }
    } finally {
      setIsGeneratingPick(false);
      setPickGenerationStep('');
      setShowPromptForm(false);
    }
  };

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // Save prompt to localStorage
    localStorage.setItem(PROMPT_KEY, prompt);

    // Generate pick
    await generatePickWithFeedback(prompt, isLoggedIn ? email : undefined);
  };

  const handleEmailSubmit = async (emailInput: string): Promise<{ success: boolean; error?: string }> => {
    setSaving(true);
    try {
      // First check if account already exists to prevent overwriting
      const existingAccount = await getAccountDetails(emailInput);
      if (existingAccount) {
        return {
          success: false,
          error: '❌ Účet s touto emailovou adresou již existuje.'
        };
      }

      // Get the current anonymous pick hash if exists
      const anonymousPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);

      // Try to save AI prompt with email (creating new account)
      await setAIPrompt(emailInput, prompt);

      // If user has anonymous pick, link it to their new account
      const hasAnonymousPick = anonymousPickHash && news.length > 0;
      if (hasAnonymousPick) {
        try {
          await linkAnonymousPickToUser(emailInput, anonymousPickHash);
        } catch (error) {
          console.warn('Failed to link anonymous pick to user:', error);
          // Don't fail account creation if linking fails
        }
      }

      // Save to localStorage
      localStorage.setItem(EMAIL_KEY, emailInput);
      setEmail(emailInput);
      setIsLoggedIn(true);

      // Clear anonymous localStorage data since we're now registered
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      // If we had anonymous articles and linked them, keep displaying them
      // Otherwise load user data from backend
      if (!hasAnonymousPick) {
        await loadUserData(emailInput);
      }
      // If we had anonymous articles, they stay displayed and are now linked to the account

      setShowEmailModal(false);
      setFeedback({
        type: 'success',
        message: '✅ Tvůj účet byl vytvořen! Prompt je uložen pro příští návštěvy.'
      });

      return { success: true };

    } catch (error) {
      console.error('Error saving email:', error);
      // Check if email already exists
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('already exists') || errorMessage.includes('duplicate')) {
        // Auto-login if email exists
        try {

          localStorage.setItem(EMAIL_KEY, emailInput);
          setEmail(emailInput);
          setIsLoggedIn(true);

          // Clear anonymous localStorage data
          localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
          localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

          // Load existing user data
          await loadUserData(emailInput);

          setShowEmailModal(false);
          setFeedback({
            type: 'success',
            message: '✅ Přihlášeni! Našli jsme tvůj existující účet.'
          });

          return { success: true };
        } catch (loginError) {
          return {
            success: false,
            error: 'Nastala chyba při přihlašování. Zkus to prosím znovu.'
          };
        }
      } else {
        return {
          success: false,
          error: 'Nastala chyba při ukládání. Zkus to prosím znovu.'
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
      // Save the updated prompt
      await setAIPrompt(email, editedPrompt);
      setPrompt(editedPrompt);
      setIsEditingPrompt(false);

      // Try to generate pick with new prompt - backend will handle daily limits
      await generatePickWithFeedback(editedPrompt, email);
    } catch (error) {
      console.error('❌ Error saving prompt:', error);
      setFeedback({
        type: 'error',
        message: '❌ Nastala chyba při ukládání. Zkus to prosím znovu.'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditingPrompt(false);
    setEditedPrompt('');
  };

  const handleLogin = async (loginEmail: string) => {
    setSaving(true);
    try {
      // Try to get account details
      const accountDetails = await getAccountDetails(loginEmail);

      if (!accountDetails) {
        setFeedback({
          type: 'error',
          message: '❌ Účet s touto emailovou adresou neexistuje.'
        });
        return;
      }

      // Save to localStorage and set logged in state
      localStorage.setItem(EMAIL_KEY, loginEmail);
      setEmail(loginEmail);
      setIsLoggedIn(true);
      setShowLoginForm(false);
      setShowPromptForm(false);

      // Load user data
      await loadUserData(loginEmail);

      setFeedback({
        type: 'success',
        message: '✅ Úspěšně přihlášeni! Vítejte zpět.'
      });

    } catch (error) {
      console.error('Error logging in:', error);
      setFeedback({
        type: 'error',
        message: '❌ Nastala chyba při přihlašování. Zkus to prosím znovu.'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleModalLogin = async (loginEmail: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Try to get account details
      const accountDetails = await getAccountDetails(loginEmail);

      if (!accountDetails) {
        return {
          success: false,
          error: '❌ Účet s touto emailovou adresou neexistuje.'
        };
      }

      // Save to localStorage and set logged in state
      localStorage.setItem(EMAIL_KEY, loginEmail);
      setEmail(loginEmail);
      setIsLoggedIn(true);

      // Clear anonymous localStorage data
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      // Load user data
      await loadUserData(loginEmail);

      setShowEmailModal(false);
      setFeedback({
        type: 'success',
        message: '✅ Úspěšně přihlášeni! Vítejte zpět.'
      });

      return { success: true };

    } catch (error) {
      console.error('Error logging in:', error);
      return {
        success: false,
        error: '❌ Nastala chyba při přihlašování. Zkus to prosím znovu.'
      };
    }
  };

  // Email change is not allowed for logged-in users
  // const handleChangeEmail = () => {
  //   localStorage.removeItem(EMAIL_KEY);
  //   setEmail('');
  //   setIsLoggedIn(false);
  //   setShowPromptForm(true);
  //   setNews([]);

  const categories = ['AI Feed', 'Vše', ...topics.map(topic => topic.name)];

  return (
    <div className="min-h-screen flex flex-col" style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Header categories={categories} activeCategory="AI Feed" />

      <main className="max-w-5xl mx-auto px-4 py-8 w-full flex-grow">
        {/* Hero Section - show for new users or when editing prompt */}
        {(showPromptForm && !isLoggedIn) && (
          <div className="text-center mb-8">
            <div className="inline-flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center">
                <span className="text-2xl">🧠</span>
              </div>
              <h1 className="text-4xl font-bold text-white">
                Tvoje denní dávka novinek!
              </h1>
            </div>
            <p className="text-blue-100 text-lg max-w-2xl mx-auto">
              Náš chytrý novinář vybere jenom ty zprávy, které tě opravdu zajímají. Napiš mu jaké zprávy bys chtěl dostávat.
            </p>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          {feedback && <FeedbackComponent feedback={feedback} />}

          {isGeneratingPick && <LoadingPickGeneration pickGenerationStep={pickGenerationStep} />}

          {showLoginForm ? (
            <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-8 border border-green-200">
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl text-white">🔐</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                  Přihlásit se do účtu
                </h2>
                <p className="text-gray-600 text-lg">
                  Zadejte emailovou adresu spojenou s tvým účtem
                </p>
              </div>

              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const loginEmail = formData.get('loginEmail') as string;
                if (loginEmail?.trim()) {
                  handleLogin(loginEmail.trim());
                }
              }} className="space-y-6">
                <div>
                  <label htmlFor="loginEmail" className="block text-lg font-semibold text-gray-800 mb-3">
                    📧 Emailová adresa
                  </label>
                  <input
                    type="email"
                    id="loginEmail"
                    name="loginEmail"
                    className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                    placeholder="vas@email.cz"
                    required
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-4 rounded-xl hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg cursor-pointer"
                  >
                    {saving ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
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
                    className="px-8 py-4 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-colors text-gray-700 font-medium cursor-pointer"
                  >
                    Zpět
                  </button>
                </div>
              </form>

              <div className="mt-6 text-center">
                <p className="text-gray-600 text-sm">
                  Nemáte ještě účet?{' '}
                  <button
                    onClick={() => {
                      setShowLoginForm(false);
                      setShowPromptForm(true);
                    }}
                    className="text-blue-600 hover:text-blue-800 font-medium cursor-pointer"
                  >
                    Vytvořte si nový
                  </button>
                </p>
              </div>
            </div>
          ) : showPromptForm ? (
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-200">
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl text-white">✨</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                  {isLoggedIn ? 'Upravte své preference' : 'Co tě zajímá?'}
                </h2>
                <p className="text-gray-600 text-lg">
                  Popiš v přirozeném jazyce, co tě zajímá. AI bude vybírat jen ty články, které jsou pro tebe relevantní.
                </p>
              </div>

              <form onSubmit={handlePromptSubmit} className="space-y-6">
                <div>
                  <label htmlFor="prompt" className="block text-lg font-semibold text-gray-800 mb-3">
                    💭 Co tě zajímá?
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={5}
                    className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg resize-none"
                    placeholder="Například: Chci mít přehled o všech kulturních akcích v Praze a jenom ty nejdůležitější celosvětové zprávy z oblasti technologií a byznysu."
                    required
                  />
                  <div className="mt-3 flex items-start space-x-2">
                    <span className="text-blue-500">💡</span>
                    <p className="text-sm text-gray-600">
                      <strong>Tip:</strong> Buďte konkrétní! Můžete zadat témata, regiony, typy zpráv nebo dokonce tón článků, který preferujete.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={saving || isGeneratingPick}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg cursor-pointer"
                  >
                    {saving || isGeneratingPick ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>{saving ? 'Ukládám...' : 'Vytvářím...'}</span>
                      </div>
                    ) : (
                      <span>🚀 {isLoggedIn ? 'Aktualizovat AI Feed' : 'Vytvořit AI Feed'}</span>
                    )}
                  </button>
                  {isLoggedIn && (
                    <button
                      type="button"
                      onClick={() => setShowPromptForm(false)}
                      className="px-8 py-4 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-colors text-gray-700 font-medium cursor-pointer"
                    >
                      Zrušit
                    </button>
                  )}
                </div>

                {/* Login option for first-time visitors */}
                {!isLoggedIn && (
                  <div className="mt-6 text-center">
                    <p className="text-gray-600 text-sm mb-2">
                      Už máte účet?
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        setShowPromptForm(false);
                        setShowLoginForm(true);
                      }}
                      className="text-blue-600 hover:text-blue-800 font-medium cursor-pointer underline"
                    >
                      Přihlásit se do existujícího účtu
                    </button>
                  </div>
                )}
              </form>
            </div>
          ) : (
            <div className="space-y-8">

              {/* Settings Bar - only for anonymous users */}
              {!isLoggedIn && prompt && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl px-6 py-4 flex items-center justify-between border border-blue-200">
                  <div className="flex items-center space-x-3">
                    <span className="text-blue-600">👤</span>
                    <span className="text-gray-700 font-medium">Anonymní uživatel</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Dočasný účet</span>
                  </div>
                  <button
                    onClick={() => setShowEmailModal(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 font-semibold text-sm cursor-pointer"
                  >
                    💾 Vytvořit účet
                  </button>
                </div>
              )}


              {/* Show current prompt for both logged in and anonymous users */}
              {prompt && (
                <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-8 border border-green-200">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-600 rounded-xl flex items-center justify-center">
                        <span className="text-xl text-white">🎯</span>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-800">Tvá perzonalizovaná preference</h3>
                        <div className="flex items-center space-x-2">
                          <p className="text-gray-600">
                            {isLoggedIn ? 'Podle toho AI vybírá tvé články' : 'AI vybralo články podle tohoto promptu'}
                          </p>
                          {isLoggedIn && email && (
                            <>
                              <span className="text-gray-400">•</span>
                              <span className="text-sm text-gray-500">{email}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    {isLoggedIn && (
                      <button
                        onClick={handleEditPrompt}
                        className="bg-white border-2 border-gray-300 hover:border-blue-400 px-4 py-2 rounded-xl transition-all hover:shadow-md flex items-center space-x-2 text-gray-700 hover:text-blue-600 cursor-pointer"
                      >
                        <span>✏️</span>
                        <span className="font-medium">Upravit</span>
                      </button>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-6 border border-gray-200">
                    {isEditingPrompt ? (
                      <div className="space-y-4">
                        <div className="flex items-start space-x-3">
                          <span className="text-blue-500 text-xl mt-1">✏️</span>
                          <div className="flex-1">
                            <textarea
                              value={editedPrompt}
                              onChange={(e) => setEditedPrompt(e.target.value)}
                              rows={4}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg resize-none"
                              placeholder="Popiš, co tě zajímá..."
                            />
                          </div>
                        </div>
                        <div className="flex items-center justify-end space-x-3">
                          <button
                            onClick={handleCancelEdit}
                            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700 cursor-pointer"
                          >
                            Zrušit
                          </button>
                          <button
                            onClick={handleSavePrompt}
                            disabled={saving || !editedPrompt.trim()}
                            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold cursor-pointer"
                          >
                            {saving ? 'Ukládám...' : 'Uložit'}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start space-x-3">
                        <span className="text-green-500 text-xl">💭</span>
                        <div className="flex-1">
                          <p className="text-gray-800 text-lg leading-relaxed">
                            {prompt}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* News section */}
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-flex items-center space-x-3 bg-blue-50 px-6 py-4 rounded-2xl border border-blue-200">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-blue-800 font-medium">
                      Načítám tvé články...
                    </span>
                  </div>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-600 rounded-xl flex items-center justify-center">
                        <span className="text-white">📰</span>
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-gray-800">Tvůj AI výběr</h2>
                        <p className="text-gray-600">
                          {news.length > 0 ? `${news.length} ${news.length === 1 ? 'nejnovější článek' : news.length >= 2 && news.length <= 4 ? 'nejnovější články' : 'nejnovějších článků'} podle tvých preferencí` : 'Žádné články nebyly nalezeny pro tvůj prompt'}
                        </p>
                        {originalPrompt && (
                          <p className="text-sm text-gray-500 mt-1">
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

      {/* Email Modal */}
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
