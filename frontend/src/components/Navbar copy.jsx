import React from "react";

export default function Navbar({ onOpenChat, hideNav = false }) {
  return (
    // Sticky transparent container
    <header
      className={
        // base sticky nav positioning
        "sticky top-0 z-50 flex justify-center pt-3 pb-2 transition-opacity duration-150 " +
        // when chatOpen == true, hide/fade and disable pointer events
        (hideNav
          ? "opacity-0 pointer-events-none"
          : "opacity-100 pointer-events-auto")
      }
    >
      {/* Centered rounded nav bar */}
      <div
        className="
          mx-auto
          max-w-6xl
          w-[calc(100%-1rem)]
          rounded-xl
          bg-white/70
          backdrop-blur
          ring-1 ring-slate-200/60
          shadow-sm
          px-4 py-3
          flex flex-col sm:flex-row sm:items-center sm:justify-between
          gap-3
        "
      >
        {/* Left: Logo + tagline */}
        <div className="flex items-start gap-3">
          <img
            src="/logos/atlas-mark-dark-bg.png"
            alt="Atlas Logo"
            className="h-10 w-10 object-contain drop-shadow-[0_1px_2px_rgba(0,0,0,0.25)]"
          />
          <div className="leading-tight">
            <div className="text-slate-800 text-base font-semibold tracking-tight">
              ATLAS
            </div>
            <div className="text-[11px] tracking-wide text-[#4d7c9e] ">
              AI built for <span className="italic">your</span> business.
            </div>
          </div>
        </div>

        {/* Right: nav links */}
        <nav className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[15px] font-medium text-slate-700 tracking-tight">
          <a
            href="#about"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            About Atlas
          </a>

          <a
            href="#supply-chain"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            Atlas for Supply Chain
          </a>

          <a
            href="#everyday-businesses"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            Atlas for Everyday Businesses
          </a>

          <a
            href="#how-it-works"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            How Atlas Works
          </a>

          <a
            href="#under-the-hood"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            AI Architecture & Stack
          </a>

          <a
            href="#behind-atlas"
            className="relative sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:w-0 sm:after:h-[2px] sm:after:bg-gradient-to-r from-blue-600 to-teal-500 sm:hover:after:w-full sm:focus:after:w-full sm:active:after:w-full sm:after:transition-all sm:after:duration-300 hover:text-slate-900 focus:text-slate-900 active:text-slate-900 transition-colors rounded-lg px-3 py-1.5 border border-slate-200 bg-white/60 shadow-sm hover:bg-white hover:border-slate-300 active:bg-slate-50 sm:border-0 sm:bg-transparent sm:shadow-none sm:px-0 sm:py-0 sm:rounded-none"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            Contact me
          </a>

          {/* CTA pill */}
          <button
            type="button"
            onClick={onOpenChat}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-3 py-1.5 text-white text-[14px] font-semibold shadow-sm hover:brightness-110 transition focus:outline-none focus:ring-4 focus:ring-blue-300/40"
          >
            <img
              src="/logos/atlas-mark-dark-bg.png"
              alt="Atlas Logo"
              className="h-4 w-4 object-contain filter brightness-0 invert opacity-90"
            />
            <span>Try Atlas</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
