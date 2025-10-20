"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

// Storage keys (same as in PersonalFeedPage)
const EMAIL_KEY = "news_app_user_email";
const PROMPT_KEY = "news_app_user_prompt";
const ANONYMOUS_PICK_HASH_KEY = "news_app_anonymous_pick_hash";
const ANONYMOUS_PICK_DATE_KEY = "news_app_anonymous_pick_date";

function DeleteAccountContent() {
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
        const params = new URLSearchParams();
        params.append("token", token);

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/account/execute-deletion`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: params.toString(),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || "Něco se pokazilo");
        }

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

          {status === "error" && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">❌</div>
              <h1 className="text-3xl font-bold text-red-600 mb-4">Chyba při mazání účtu</h1>
              <p className="text-lg text-gray-600 mb-8">{message}</p>
              <a href="/" className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-8 rounded-xl transition-all">
                Přejít na hlavní stránku
              </a>
            </div>
          )}
        </div>
      </main>

      <Footer categories={categories} />
    </div>
  );
}

export default function DeleteAccountPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
    </div>}>
      <DeleteAccountContent />
    </Suspense>
  );
}
