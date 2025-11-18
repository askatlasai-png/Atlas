// src/pages/HowAtlasWorks.jsx
import React from "react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar.jsx";
import { UploadCloud, Braces, MessageCircle, CheckCircle2 } from "lucide-react";
import TechStack from "@/sections/about/TechStack.jsx";


export default function HowAtlasWorksPage() {
  const steps = [
    {
      icon: UploadCloud,
      title: "Connect to live operational data",
      desc:
        "Atlas plugs into the systems you already run — ERP, inventory, purchasing, POS, and service logs — without ripping anything out.",
    },
    {
      icon: Braces,
      title: "Builds business context, not just tables",
      desc:
        "It understands which PO feeds which order, which supplier is slipping, and which locations or machines are at risk.",
    },
    {
      icon: MessageCircle,
      title: "You ask in plain English",
      desc:
        "Planners, buyers, and operators can simply ask what is late, what is at risk, and what needs attention next — no SQL, no dashboards.",
    },
    {
      icon: CheckCircle2,
      title: "You get a clear answer you can act on",
      desc:
        "Atlas returns a concise summary, key risks, and recommended actions — with a transparent trail back to the underlying rows and tables.",
    },
  ];

  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-gradient-to-b from-slate-50 via-blue-50/40 to-blue-100/20 text-slate-900">
        <div className="mx-auto max-w-6xl px-4 pb-20 pt-14 md:pt-16 space-y-14 md:space-y-16">
          {/* Page header */}
          <section className="text-center max-w-3xl mx-auto">
            <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-blue-700">
              How Atlas Works
            </p>
            <h1 className="mt-3 text-3xl md:text-4xl font-semibold leading-tight text-slate-900">
              From scattered systems to a clear answer your team can trust.
            </h1>
            <p className="mt-3 text-sm md:text-base text-slate-600 leading-relaxed">
              Atlas connects to the systems you already run, keeps the operational context,
              and turns it into answers you can actually use — with a transparent trail
              back to your underlying data.
            </p>

            <div className="mt-5 flex justify-center">
              <div className="h-px w-24 bg-gradient-to-r from-blue-500 via-cyan-400 to-teal-400 rounded-full" />
            </div>
          </section>

          {/* UNDER THE HOOD */}
          <section className="grid gap-6 md:gap-10 md:grid-cols-[minmax(0,190px),minmax(0,1fr)] items-start">
            {/* Left rail label */}
            <div className="md:text-right">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-blue-700">
                Under the Hood
              </p>
              <p className="mt-2 hidden text-xs text-slate-500 md:block">
                How Atlas is architected so operators can trust every answer.
              </p>
            </div>

            {/* Card */}
            <div className="rounded-2xl bg-white/95 backdrop-blur-sm shadow-[0_18px_45px_rgba(15,23,42,0.08)] ring-1 ring-slate-200/80 p-6 md:p-8">
              <h2 className="text-xl md:text-2xl font-semibold text-slate-900">
                Built like an AI product, not a dashboard.
              </h2>
              <p className="mt-3 text-sm md:text-[15px] leading-relaxed text-slate-600">
                Atlas combines retrieval, reasoning, and domain-aware guardrails to deliver
                answers you can trust. It is designed for live operations — not demo data
                or vanity charts.
              </p>

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Retrieval grounded in your data
                  </p>
                  <p className="mt-1 text-sm text-slate-600">
                    Multi-source retrieval across ERP tables, reports, and file-based context,
                    so answers are always backed by real transactions.
                  </p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Domain-aware reasoning
                  </p>
                  <p className="mt-1 text-sm text-slate-600">
                    Supply chain–specific logic to reason about POs, SOs, on-hand, lead times,
                    and constraints — not just generic chat.
                  </p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Guardrails for real operations
                  </p>
                  <p className="mt-1 text-sm text-slate-600">
                    Controls to keep answers traceable, auditable, and safe for planners,
                    buyers, and operations leaders to act on.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* HOW ATLAS TURNS DATA INTO ANSWERS */}
          <section className="grid gap-6 md:gap-10 md:grid-cols-[minmax(0,190px),minmax(0,1fr)] items-start">
            {/* Left rail label */}
            <div className="md:text-right">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-blue-700">
                The Atlas Flow
              </p>
              <p className="mt-2 hidden text-xs text-slate-500 md:block">
                The high-level flow from raw data to an answer with clear next steps.
              </p>
            </div>

            {/* Card */}
            <div className="rounded-2xl bg-white/95 backdrop-blur-sm shadow-[0_18px_45px_rgba(15,23,42,0.08)] ring-1 ring-slate-200/80 p-6 md:p-8">
              <h2 className="text-xl md:text-2xl font-semibold text-slate-900">
                How Atlas turns your data into real answers.
              </h2>
              <p className="mt-3 text-sm md:text-[15px] leading-relaxed text-slate-600">
                These steps outline how Atlas pulls from your systems, keeps the business
                context, and returns an answer your team can act on — in plain language.
              </p>

              {/* Steps grid */}
              <div className="mt-6 grid gap-4 md:grid-cols-2">
                {steps.map((step) => (
                  <div
                    key={step.title}
                    className="flex gap-3 rounded-xl border border-slate-100 bg-slate-50/60 p-4"
                  >
                    <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 ring-1 ring-blue-100">
                      <step.icon className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">
                        {step.title}
                      </p>
                      <p className="mt-1 text-xs md:text-sm text-slate-600 leading-relaxed">
                        {step.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* TECH STACK */}
          {/* TECH STACK */}
            <section className="grid gap-6 md:gap-10 md:grid-cols-[minmax(0,190px),minmax(0,1fr)] items-start">
            {/* Left rail label */}
            <div className="md:text-right">
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-blue-700">
                Tech Stack
                </p>
                <p className="mt-2 hidden text-xs text-slate-500 md:block">
                Frameworks and infrastructure behind Atlas.
                </p>
            </div>

            {/* Your existing TechStack card with icons */}
            <TechStack />
            </section>


          {/* In-page CTA */}
          <section className="pt-4 text-center">
            <p className="text-sm text-slate-600">
              Want to see these pieces working together on real supply chain data?
            </p>
            <button
              type="button"
              onClick={() => {
                if (typeof window !== "undefined") {
                  const url = new URL(window.location.origin);
                  url.searchParams.set("openChat", "1");
                  url.hash = "see-atlas-in-action";
                  window.location.href = url.toString();
                }
              }}
              className="mt-3 inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
            >
              <span>Try Atlas on sample data</span>
            </button>
          </section>
        </div>

        {/* Floating Try Atlas button */}
        <div className="fixed right-3 bottom-3 sm:right-6 sm:bottom-6 z-40">
          <Link
            to="/?openChat=1#see-atlas-in-action"
            className="inline-flex items-center gap-2 sm:gap-3 rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-4 py-2.5 sm:px-6 sm:py-3 text-sm sm:text-base font-semibold text-white shadow-lg hover:brightness-110 transition-transform focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            <img
              src="/logos/atlas-mark-dark-bg.png"
              alt="Atlas Logo"
              className="h-5 w-5 sm:h-6 sm:w-6 object-contain filter brightness-0 invert opacity-90"
            />
            <span className="hidden sm:inline">Try Atlas Now</span>
            <span className="sm:hidden">Try Atlas</span>
          </Link>
        </div>
      </main>
    </>
  );
}
