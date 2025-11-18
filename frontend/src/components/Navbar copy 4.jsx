import React from "react";
import { Link } from "react-router-dom";

export default function Navbar({ onOpenChat, hideNav = false }) {
  const handleTryAtlas = () => {
    if (typeof onOpenChat === "function") {
      onOpenChat();
    } else if (typeof window !== "undefined") {
      const url = new URL(window.location.origin);
      url.searchParams.set("openChat", "1");
      url.hash = "see-atlas-in-action";
      window.location.href = url.toString();
    }
  };

  // Unified link class: pill on mobile, clean with underline on desktop
  const linkClass = `
    relative
    inline-flex items-center
    rounded-lg bg-slate-50 px-2 py-1 text-[13px] text-slate-700
    hover:bg-slate-100 hover:text-slate-900 transition-colors
    sm:bg-transparent sm:px-0 sm:py-0 sm:rounded-none sm:hover:bg-transparent
    sm:after:absolute sm:after:-bottom-1 sm:after:left-0 sm:after:h-[2px] sm:after:w-0
    sm:after:bg-gradient-to-r sm:after:from-blue-600 sm:after:via-cyan-500 sm:after:to-teal-500
    sm:hover:after:w-full sm:after:transition-all sm:after:duration-300
  `;

  return (
    <header
      className={
        "sticky top-0 z-50 flex justify-center pt-3 pb-2 transition-opacity duration-150 " +
        (hideNav
          ? "opacity-0 pointer-events-none"
          : "opacity-100 pointer-events-auto")
      }
    >
      <div
        className="
          mx-auto max-w-6xl w-[calc(100%-1rem)]
          rounded-xl bg-white/70 backdrop-blur
          ring-1 ring-slate-200 shadow-sm
          px-4 py-3
          flex flex-col sm:flex-row sm:items-center sm:justify-between
          gap-3
        "
      >
        {/* LEFT: Logo + tagline (clickable to go home) */}
        <Link
          to="/"
          className="flex items-start gap-3 cursor-pointer group"
        >
          <img
            src="/logos/atlas-mark-dark-bg.png"
            alt="Atlas Logo"
            className="h-10 w-10 object-contain drop-shadow-[0_1px_2px_rgba(0,0,0,0.25)] group-hover:scale-[1.02] transition-transform"
          />
          <div className="leading-tight">
            <div className="text-slate-800 text-base font-semibold tracking-tight">
              ATLAS
            </div>
            <div className="text-[11px] tracking-wide text-[#4d7c9e]">
              AI built for <span className="italic">your</span> business.
            </div>
          </div>
        </Link>


        {/* RIGHT: Nav links + CTA */}
        <div className="flex flex-wrap items-center justify-end gap-x-6 gap-y-2 sm:gap-x-8 sm:pr-2">
          {/* Nav links */}
          <nav className="flex flex-wrap items-center gap-x-5 sm:gap-x-8 gap-y-1 text-[13px] font-medium">
            <a href="/#about" className={linkClass}>
              About Atlas
            </a>

            <a href="/#supply-chain" className={linkClass}>
              Atlas for Supply Chain
            </a>

            <a href="/#everyday-businesses" className={linkClass}>
              Atlas for Everyday Businesses
            </a>

            <Link to="/how-atlas-works" className={linkClass}>
              How Atlas Works
            </Link>

            <a href="/#behind-atlas" className={linkClass}>
              Contact me
            </a>
          </nav>

          {/* CTA */}
          <button
            type="button"
            onClick={handleTryAtlas}
            className="
              inline-flex items-center gap-2
              rounded-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500
              px-4 py-1.5 text-[13px] font-semibold text-white
              shadow-sm transition hover:brightness-110
              focus:outline-none focus:ring-4 focus:ring-blue-300/40
            "
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
    </header>
  );
}
