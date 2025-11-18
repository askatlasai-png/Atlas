import React from "react";
import { Link } from "react-router-dom";

export default function Navbar({ onOpenChat, hideNav = false }) {
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
        {/* LEFT — Logo */}
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
            <div className="text-[11px] tracking-wide text-[#4d7c9e]">
              AI built for <span className="italic">your</span> business.
            </div>
          </div>
        </div>

        {/* RIGHT — Nav Links */}
        <nav className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[15px] font-medium text-slate-700 tracking-tight">

          {/* Home Page Anchors */}
          <a
            href="/#about"
            className="nav-link"
          >
            About Atlas
          </a>

          <a
            href="/#supply-chain"
            className="nav-link"
          >
            Atlas for Supply Chain
          </a>

          <a
            href="/#everyday-businesses"
            className="nav-link"
          >
            Atlas for Everyday Businesses
          </a>



          {/* NEW: Architecture Page */}
          <Link
            to="/how-atlas-works"
            className="nav-link"
          >
            How Atlas Works
          </Link>

          <a
            href="/#behind-atlas"
            className="nav-link"
          >
            Contact me
          </a>


          {/* CTA Pill */}
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
