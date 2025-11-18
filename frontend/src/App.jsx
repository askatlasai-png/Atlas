import AtlasChatUI from './components/AtlasChatUI'
import React from "react";
import { Routes, Route } from "react-router-dom";
import AtlasShowcase from "./pages/AtlasShowcase.jsx"; // <-- add this
import ExploreAtlas from "./sections/about/ExploreAtlas.jsx";
import HowAtlasWorksPage from "@/pages/HowAtlasWorks.jsx";



export default function App() {
  return (
    <Routes>
      {/* Home / main landing */}
      <Route path="/" element={<AtlasShowcase />} />

      {/* Optional alias if you want /atlas to go to the same page */}
      <Route path="/atlas" element={<AtlasShowcase />} />

      {/* Explore page (if you still use it) */}
      <Route path="/explore" element={<ExploreAtlas />} />

      {/* NEW: How Atlas Works page */}
      <Route path="/how-atlas-works" element={<HowAtlasWorksPage />} />
    </Routes>
  );
}