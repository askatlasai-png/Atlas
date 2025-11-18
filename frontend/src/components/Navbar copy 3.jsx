import React from "react";
import { Link } from "react-router-dom";

export default function Navbar({ onOpenChat, hideNav = false }) {
  const handleTryAtlas = () => {
    if (typeof onOpenChat === "function") {
      // Home page: open the chat modal
      onOpenChat();
    } else if (typeof window !== "undefined") {
      // Other pages: go to main page and signal it to open chat
      const url = new URL(window.location.origin);
      url.searchParams.set("openChat", "1");
      url.hash = "see-atlas-in-action";
      window.location.href = url.toString();
    }
  };

  return (
    <header
      className={
        "sticky top-0 z-50 flex justify-center pt-3 pb-2 transition-opacity duration-150 " +
        (hideNav
          ? "opacity-0 pointer-events-none"
          : "opacity-100 pointer-events-auto")
      }
    >
      <div className="mx-auto w-[calc(100%-1rem)] max-w-6xl rounded-xl bg-white/80 px-4 py-3 shadow-sm ring-1 ring-slate-200/70 backdrop-blur">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          {/* LEFT: Logo + wordmark */}
          <div className="flex items-center gap-3">
            <img
              src="/logos/atlas-mark-dark-bg.png"
              alt="Atlas Logo"
              className="h-9 w-9 object-contain drop-shadow-[0_1px_2px_rgba(0,0,0,0.35)]"
            />
            <div className="leading-tight">
              <div className="text-sm font-semibold tracking-tight text-slate-900">
                ATLAS
              </div>
              <div className="text-[11px] tracking-wide text-[#4d7c9e]">
                AI built for <span className="italic">your</span> business.
              </div>
            </div>
          </div>

          {/* RIGHT: Nav + CTA (stacked on mobile, inline on desktop) */}
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
            {/* Nav links */}
            <nav className="flex flex-wrap items-center gap-2 text-[12px] sm:text-[13px] font-medium text-slate-700">
              <a
                href="/#about"
                className="rounded-lg bg-slate-50 px-2 py-1 sm:bg-transparent sm:px-0 sm:py-0 sm:hover:text-slate-900"
              >
                About Atlas
              </a>

              <a
                href="/#supply-chain"
                className="rounded-lg bg-slate-50 px-2 py-1 sm:bg-transparent sm:px-0 sm:py-0 sm:hover:text-slate-900"
              >
                Atlas for Supply Chain
              </a>

              <a
                href="/#everyday-businesses"
                className="rounded-lg bg-slate-50 px-2 py-1 sm:bg-transparent sm:px-0 sm:py-0 sm:hover:text-slate-900"
              >
                Atlas for Everyday Businesses
              </a>

              <Link
                to="/how-atlas-works"
                className="rounded-lg bg-slate-50 px-2 py-1 sm:bg-transparent sm:px-0 sm:py-0 sm:hover:text-slate-900"
              >
                How Atlas Works
              </Link>

              <a
                href="/#behind-atlas"
                className="rounded-lg bg-slate-50 px-2 py-1 sm:bg-transparent sm:px-0 sm:py-0 sm:hover:text-slate-900"
              >
                Contact me
              </a>
            </nav>

            {/* CTA pill */}
            <button
              type="button"
              onClick={handleTryAtlas}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-3 py-1.5 text-[13px] font-semibold text-white shadow-sm transition hover:brightness-110 focus:outline-none focus:ring-4 focus:ring-blue-300/40"
            >
              <img
                src="/logos/atlas-mark-dark-bg.png"
                alt="Atlas Logo"
                className="h-4 w-4 object-contain filter brightness-0 invert opacity-90"
              />
              <span>Try Atlas</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
