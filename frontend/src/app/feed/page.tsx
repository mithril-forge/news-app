'use client'

import { useState, useEffect } from 'react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import ArticleCard from '@/components/news/ArticleCard';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Alert, AlertDescription } from '~/components/ui/alert';
import { Badge } from '~/components/ui/badge';
import { Separator } from '~/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '~/components/ui/dialog';
import { Brain, Sparkles, Mail, Loader2, CheckCircle2, AlertCircle, Info, Pencil } from 'lucide-react';
import { fetchTopics, getAccountDetails, setAIPrompt, getAllLatestPick, getPickNews } from '@/services/api';
import { generatePick, linkAnonymousPickToUser } from '@/services/api/feed';
import { NewsArticle, Topic } from '@/types';

// Storage keys
const EMAIL_KEY = 'news_app_user_email';
const PROMPT_KEY = 'news_app_user_prompt';
const ANONYMOUS_PICK_HASH_KEY = 'news_app_anonymous_pick_hash';
const ANONYMOUS_PICK_DATE_KEY = 'news_app_anonymous_pick_date';

type FeedbackType = 'success' | 'error' | 'info' | 'warning' | null;

interface FeedbackMessage {
  type: FeedbackType;
  message: string;
}

export default function PersonalFeedPage() {
  const [email, setEmailState] = useState('');
  const [prompt, setPrompt] = useState('');
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showEmailDialog, setShowEmailDialog] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null);
  const [isGeneratingPick, setIsGeneratingPick] = useState(false);
  const [showPromptForm, setShowPromptForm] = useState(true);
  const [isEditingPrompt, setIsEditingPrompt] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState('');
  const [dialogEmail, setDialogEmail] = useState('');
  const [dialogError, setDialogError] = useState('');

  // Load saved data
  useEffect(() => {
    const savedEmail = localStorage.getItem(EMAIL_KEY);
    const savedPrompt = localStorage.getItem(PROMPT_KEY);
    const savedPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);
    const savedPickDate = localStorage.getItem(ANONYMOUS_PICK_DATE_KEY);

    if (savedEmail) {
      setEmailState(savedEmail);
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
      if (accountDetails?.prompt) {
        setPrompt(accountDetails.prompt);
        const pickResponse = await getAllLatestPick(userEmail);
        setNews(pickResponse.articles);

        if (pickResponse.articles.length === 0) {
          setFeedback({
            type: 'warning',
            message: 'Tvůj prompt byl příliš specifický. Zkus být obecnější.'
          });
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

      if (pickResponse.articles.length === 0) {
        setFeedback({
          type: 'warning',
          message: 'Nenašli jsme žádné odpovídající články. Zkus jiný prompt.'
        });
      }
    } catch (error) {
      console.error('Error loading pick:', error);
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);
    } finally {
      setLoading(false);
    }
  };

  const generatePickWithFeedback = async (userPrompt: string, userEmail?: string) => {
    setIsGeneratingPick(true);
    setFeedback(null);

    try {
      if (userEmail) {
        await generatePick({ userEmail });
        await loadUserData(userEmail);
      } else {
        const response = await generatePick({ prompt: userPrompt });
        const pickResponse = await getPickNews(response.hash);
        setNews(pickResponse.articles);

        const today = new Date().toDateString();
        localStorage.setItem(ANONYMOUS_PICK_HASH_KEY, response.hash);
        localStorage.setItem(ANONYMOUS_PICK_DATE_KEY, today);

        if (pickResponse.articles.length === 0) {
          setFeedback({
            type: 'warning',
            message: 'Nenašli jsme žádné odpovídající články. Zkus být obecnější.'
          });
          return;
        }
      }

      if (!userEmail) {
        setShowEmailDialog(true);
      }

      setFeedback({
        type: 'success',
        message: 'Tvůj AI feed je připraven! Články byly vybrány podle tvých preferencí.'
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      if (errorMessage.includes('daily limit') || errorMessage.includes('429')) {
        if (email && isLoggedIn) {
          setFeedback({
            type: 'info',
            message: 'Tvůj prompt byl aktualizován! Nové články dostaneš od zítřka.'
          });
        } else {
          setFeedback({
            type: 'warning',
            message: 'Dosáhl jsi denního limitu. Vytvoř si účet nebo zkus zítra.'
          });
        }
      } else {
        setFeedback({
          type: 'error',
          message: 'Nastala chyba. Zkus to prosím znovu za chvíli.'
        });
      }
    } finally {
      setIsGeneratingPick(false);
      setShowPromptForm(false);
    }
  };

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    localStorage.setItem(PROMPT_KEY, prompt);
    await generatePickWithFeedback(prompt, isLoggedIn ? email : undefined);
  };

  const handleEmailSubmit = async () => {
    if (!dialogEmail.trim()) return;

    setSaving(true);
    setDialogError('');

    try {
      const existingAccount = await getAccountDetails(dialogEmail);
      if (existingAccount) {
        setDialogError('Účet s tímto emailem již existuje.');
        setSaving(false);
        return;
      }

      const anonymousPickHash = localStorage.getItem(ANONYMOUS_PICK_HASH_KEY);
      await setAIPrompt(dialogEmail, prompt);

      if (anonymousPickHash && news.length > 0) {
        await linkAnonymousPickToUser(dialogEmail, anonymousPickHash);
      }

      localStorage.setItem(EMAIL_KEY, dialogEmail);
      setEmailState(dialogEmail);
      setIsLoggedIn(true);
      localStorage.removeItem(ANONYMOUS_PICK_HASH_KEY);
      localStorage.removeItem(ANONYMOUS_PICK_DATE_KEY);

      setShowEmailDialog(false);
      setFeedback({
        type: 'success',
        message: 'Tvůj účet byl vytvořen! Prompt je uložen.'
      });

    } catch (error) {
      setDialogError('Nastala chyba. Zkus to prosím znovu.');
    } finally {
      setSaving(false);
    }
  };

  const handleLogin = async () => {
    if (!dialogEmail.trim()) return;

    setSaving(true);
    setDialogError('');

    try {
      const accountDetails = await getAccountDetails(dialogEmail);

      if (!accountDetails) {
        setDialogError('Účet s tímto emailem neexistuje.');
        setSaving(false);
        return;
      }

      localStorage.setItem(EMAIL_KEY, dialogEmail);
      setEmailState(dialogEmail);
      setIsLoggedIn(true);
      setShowLoginDialog(false);
      setShowPromptForm(false);

      await loadUserData(dialogEmail);

      setFeedback({
        type: 'success',
        message: 'Úspěšně přihlášen! Vítej zpět.'
      });

    } catch (error) {
      setDialogError('Nastala chyba při přihlašování.');
    } finally {
      setSaving(false);
    }
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
      setFeedback({
        type: 'error',
        message: 'Nastala chyba při ukládání.'
      });
    } finally {
      setSaving(false);
    }
  };

  const categories = ['AI Feed', 'Vše', ...topics.map(topic => topic.name)];

  const getAlertIcon = (type: FeedbackType) => {
    switch (type) {
      case 'success':
        return CheckCircle2;
      case 'error':
        return AlertCircle;
      case 'warning':
        return AlertCircle;
      case 'info':
        return Info;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header categories={categories} activeCategory="AI Feed" />

      <main className="max-w-5xl mx-auto px-4 py-8 w-full flex-grow">
        {/* Hero Section */}
        {showPromptForm && !isLoggedIn && (
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="w-16 h-16 rounded-2xl ai-gradient flex items-center justify-center shadow-lg shadow-primary/30 animate-pulse">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-gradient">Tvůj AI Feed</h1>
            </div>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              AI vybere pouze zprávy, které tě skutečně zajímají
            </p>
          </div>
        )}

        {/* Feedback Alert */}
        {feedback && (() => {
          const Icon = getAlertIcon(feedback.type);
          return (
            <Alert className="mb-6" variant={feedback.type === 'error' ? 'destructive' : 'default'}>
              {Icon && <Icon className="h-4 w-4" />}
              <AlertDescription>{feedback.message}</AlertDescription>
            </Alert>
          );
        })()}

        {/* Loading state */}
        {isGeneratingPick && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <span className="text-muted-foreground">Vytvářím tvůj personalizovaný feed...</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Prompt Form */}
        {showPromptForm && (
          <Card className="card-elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl ai-gradient flex items-center justify-center shadow-md">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-xl">Co tě zajímá?</CardTitle>
                  <CardDescription>
                    Napiš, jaké zprávy chceš dostávat. AI vybere jen relevantní články.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePromptSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={5}
                    placeholder="Například: Chci přehled o politice v ČR a nejdůležitější zprávy z oblasti technologií a byznysu."
                    className="resize-none"
                    required
                  />
                  <p className="text-sm text-muted-foreground flex items-start gap-2">
                    <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>
                      Buď konkrétní! Pokrýváme hlavně události z ČR a světa.
                    </span>
                  </p>
                </div>

                {/* Quick prompt templates */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Nebo zkus šablonu:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {[
                      'Politika a ekonomika ČR',
                      'Technologie a věda',
                      'Sport a kultura',
                      'Světové události'
                    ].map((template) => (
                      <Button
                        key={template}
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setPrompt(`Chci denní přehled z oblasti: ${template}`)}
                        className="text-xs"
                      >
                        {template}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <Button type="submit" disabled={saving || isGeneratingPick} className="flex-1 ai-gradient">
                    {saving || isGeneratingPick ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Vytvářím...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Vytvořit AI Feed
                      </>
                    )}
                  </Button>
                  {isLoggedIn && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowPromptForm(false)}
                    >
                      Zrušit
                    </Button>
                  )}
                </div>

                {!isLoggedIn && (
                  <div className="text-center pt-4 border-t">
                    <p className="text-sm text-muted-foreground mb-2">
                      Už máte účet?
                    </p>
                    <Button
                      type="button"
                      variant="link"
                      onClick={() => setShowLoginDialog(true)}
                      className="text-primary"
                    >
                      Přihlásit se
                    </Button>
                  </div>
                )}
              </form>
            </CardContent>
          </Card>
        )}

        {/* Content shown when prompt is submitted */}
        {!showPromptForm && (
          <div className="space-y-6">
            {/* Anonymous user banner */}
            {!isLoggedIn && prompt && (
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">Anonymní</Badge>
                      <span className="text-sm text-muted-foreground">Dočasný účet</span>
                    </div>
                    <Button size="sm" onClick={() => setShowEmailDialog(true)}>
                      <Mail className="mr-2 h-4 w-4" />
                      Vytvořit účet
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Current prompt display */}
            {prompt && (
              <Card>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-md bg-primary/10 flex items-center justify-center">
                        <Brain className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle>Tvá preference</CardTitle>
                        <CardDescription>
                          {isLoggedIn ? `AI vybírá podle tohoto promptu • ${email}` : 'AI vybralo podle tohoto promptu'}
                        </CardDescription>
                      </div>
                    </div>
                    {isLoggedIn && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEditedPrompt(prompt);
                          setIsEditingPrompt(true);
                        }}
                      >
                        <Pencil className="h-4 w-4 mr-2" />
                        Upravit
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {isEditingPrompt ? (
                    <div className="space-y-4">
                      <Textarea
                        value={editedPrompt}
                        onChange={(e) => setEditedPrompt(e.target.value)}
                        rows={4}
                        className="resize-none"
                      />
                      <div className="flex gap-3">
                        <Button onClick={handleSavePrompt} disabled={saving || !editedPrompt.trim()}>
                          {saving ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Ukládám...
                            </>
                          ) : (
                            'Uložit'
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => setIsEditingPrompt(false)}
                        >
                          Zrušit
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed">{prompt}</p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* News Section */}
            {loading ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-center gap-3 py-8">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    <span className="text-muted-foreground">Načítám články...</span>
                  </div>
                </CardContent>
              </Card>
            ) : news.length > 0 ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Tvůj výběr</h2>
                    <p className="text-muted-foreground">
                      {news.length} {news.length === 1 ? 'článek' : news.length <= 4 ? 'články' : 'článků'} podle tvých preferencí
                    </p>
                  </div>
                </div>

                <div className="grid gap-6">
                  {news.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </main>

      {/* Email Dialog */}
      <Dialog open={showEmailDialog} onOpenChange={setShowEmailDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg ai-gradient flex items-center justify-center">
                <Mail className="h-5 w-5 text-white" />
              </div>
              <DialogTitle className="text-xl">Vytvořit účet</DialogTitle>
            </div>
            <DialogDescription className="text-base">
              Ulož si svůj prompt a dostávej denně personalizované zprávy na email.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="vas@email.cz"
                value={dialogEmail}
                onChange={(e) => {
                  setDialogEmail(e.target.value);
                  setDialogError('');
                }}
                className="h-11"
              />
            </div>

            {/* Show current prompt */}
            {prompt && (
              <div className="rounded-lg bg-accent/50 p-3 border border-border">
                <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wide">
                  Tvůj prompt:
                </p>
                <p className="text-sm line-clamp-2">{prompt}</p>
              </div>
            )}

            {dialogError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{dialogError}</AlertDescription>
              </Alert>
            )}
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setShowEmailDialog(false)}>
              Možná později
            </Button>
            <Button
              onClick={handleEmailSubmit}
              disabled={saving || !dialogEmail.trim()}
              className="ai-gradient"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Vytvářím účet...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Vytvořit účet
                </>
              )}
            </Button>
          </DialogFooter>

          <Separator />

          <div className="text-center text-sm text-muted-foreground">
            Už máte účet?{' '}
            <Button
              variant="link"
              className="p-0 h-auto text-primary"
              onClick={() => {
                setDialogEmail('');
                setDialogError('');
                setShowEmailDialog(false);
                setShowLoginDialog(true);
              }}
            >
              Přihlásit se
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Login Dialog */}
      <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
                <Mail className="h-5 w-5 text-primary" />
              </div>
              <DialogTitle className="text-xl">Přihlásit se</DialogTitle>
            </div>
            <DialogDescription className="text-base">
              Zadej email spojený s tvým účtem
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label htmlFor="login-email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="login-email"
                type="email"
                placeholder="vas@email.cz"
                value={dialogEmail}
                onChange={(e) => {
                  setDialogEmail(e.target.value);
                  setDialogError('');
                }}
                className="h-11"
              />
            </div>

            {dialogError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{dialogError}</AlertDescription>
              </Alert>
            )}
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setShowLoginDialog(false)}>
              Zrušit
            </Button>
            <Button onClick={handleLogin} disabled={saving || !dialogEmail.trim()}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Přihlašuji...
                </>
              ) : (
                'Přihlásit se'
              )}
            </Button>
          </DialogFooter>

          <Separator />

          <div className="text-center text-sm text-muted-foreground">
            Nemáte účet?{' '}
            <Button
              variant="link"
              className="p-0 h-auto text-primary"
              onClick={() => {
                setDialogEmail('');
                setDialogError('');
                setShowLoginDialog(false);
                setShowEmailDialog(true);
              }}
            >
              Vytvořit nový
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Footer categories={categories} />
    </div>
  );
}
