import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import MobilePromptDrawer from "./MobilePromptDrawer";

// ✅ Base API URL for backend (uses environment variable in Amplify or defaults to /api)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

// helper function for table rendering
function rowsToMarkdownTable(rows, maxRows = 50) {
  if (!Array.isArray(rows) || rows.length === 0) return "(No rows.)";
  const cols = Array.from(
    rows.reduce((s, r) => {
      Object.keys(r || {}).forEach((k) => s.add(k));
      return s;
    }, new Set())
  );

  const esc = (v) => (v == null ? "" : String(v).replace(/\|/g, "\\|"));
  const header = `| ${cols.join(" | ")} |`;
  const sep = `| ${cols.map(() => "---").join(" | ")} |`;
  const body = rows
    .slice(0, maxRows)
    .map((r) => `| ${cols.map((c) => esc(r?.[c])).join(" | ")} |`);
  const more =
    rows.length > maxRows
      ? `\n\n> Showing first ${maxRows} of ${rows.length} rows.`
      : "";
  return [header, sep, ...body].join("\n") + more;
}

function Message({ role, text }) {
  const isUser = role === "user";
  const isThinking = role === "thinking";

  let bubbleClasses =
    "prose prose-zinc rounded-2xl px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm transition-all duration-200 shadow-sm";

  if (isUser) {
    bubbleClasses +=
      " bg-white border border-slate-200 text-slate-800 max-w-[95%] sm:max-w-[88%] xl:max-w-[90%]";
  } else if (isThinking) {
    bubbleClasses +=
      " bg-gradient-to-r from-blue-50 via-cyan-50 to-teal-50 border border-cyan-200/60 text-slate-600 max-w-[85%] sm:max-w-[60%] animate-pulse-soft";
  } else {
    bubbleClasses +=
      " bg-blue-50/70 text-slate-800 max-w-[95%] sm:max-w-[88%] xl:max-w-[90%]";
  }

  return (
    <div className={`mb-3 flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={bubbleClasses}>
        {isUser ? (
          text
        ) : isThinking ? (
          <div className="flex items-center gap-2 text-[13px] text-slate-600">
            <span className="inline-block h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
            <span>thinking…</span>
          </div>
        ) : (
          <div className="overflow-x-auto max-w-full">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {text || ""}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}


// ✅ Main chat UI component
export default function AtlasChatUI({
  apiUrl = `${API_BASE_URL}/api/chat`,
  apiKey = import.meta.env.VITE_ATLAS_API_KEY,
  onContextUpdate,
  incomingPrompt,
  messages,
  setMessages,
  onPromptConsumed,
  onOpenDataSources,
  className = "",
}) {

  //
  // STATE
  //
  const [input, setInput] = useState("");

  // Combined state to ensure they update together
  const [uiState, setUIState] = useState({
    isBusy: false,
    isStreamingUI: false,
    typingFullText: ""
  });

  const isBusy = uiState.isBusy;
  const isStreamingUI = uiState.isStreamingUI;
  const typingFullText = uiState.typingFullText;

  const setIsBusy = (val) => {
    setUIState(prev => ({ ...prev, isBusy: val }));
  };

  const setIsStreamingUI = (val) => {
    setUIState(prev => ({ ...prev, isStreamingUI: val }));
  };

  const setTypingFullText = (val) => {
    setUIState(prev => ({ ...prev, typingFullText: val }));
  };

  // for highlighting injected prompt from left rail
  const [justPrefilled, setJustPrefilled] = useState(false);

  // Mobile prompt drawer state
  const [showMobileDrawer, setShowMobileDrawer] = useState(false);

  // refs that don't cause rerenders
  const isStreamingRef = useRef(false); // internal guard to stop the typewriter
  const typingTimer = useRef(null);
  const chatScrollRef = useRef(null);
  const inputRef = useRef(null);

  // scroll pinning so we auto-scroll only if user is already at bottom
  const [isPinned, setIsPinned] = useState(true);

  //
  // SCROLL MANAGEMENT
  //
  useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;
    const handleScroll = () => {
      const tolerance = 24;
      setIsPinned(
        el.scrollTop + el.clientHeight >= el.scrollHeight - tolerance
      );
    };
    el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToBottom = (force = false) => {
    const el = chatScrollRef.current;
    if (!el) return;
    if (!force && !isPinned) return;
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  };

  useLayoutEffect(() => {
    scrollToBottom(false);
  }, [messages]);

  //
  // LEFT RAIL PREFILL HANDOFF
  //
  useEffect(() => {
    if (incomingPrompt && incomingPrompt.trim() !== "") {
      setInput(incomingPrompt);
      inputRef.current?.focus();
      setJustPrefilled(true);
      const t = setTimeout(() => setJustPrefilled(false), 800);
      return () => clearTimeout(t);
    }
  }, [incomingPrompt]);

  //
  // STOP BUTTON HANDLER
  //
  const stopTyping = () => {
    onPromptConsumed?.();

    // kill future ticks
    if (typingTimer.current) {
      clearTimeout(typingTimer.current);
      typingTimer.current = null;
    }

    // stop the streaming animation
    isStreamingRef.current = false;

    // finalize assistant message with full text, and nuke "thinking"
    setMessages((m) => {
      const filtered = m.filter((msg) => msg.role !== "thinking");
      const last = filtered[filtered.length - 1];

      if (last && last.role === "assistant") {
        // Dump the complete answer immediately
        last.text = typingFullText || last.text || "";
      } else if (typingFullText) {
        // If no assistant message exists yet, create one with full text
        filtered.push({ role: "assistant", text: typingFullText });
      }

      return filtered;
    });

    // clear streaming flags/state - atomic update
    setUIState({
      isBusy: false,
      isStreamingUI: false,
      typingFullText: ""
    });

    scrollToBottom(true);
    inputRef.current?.focus();
  };

  //
  // DISPLAY ANSWER WITH TYPING EFFECT
  //
  const beginStreaming = (finalTextRaw) => {
    const finalText = (finalTextRaw ?? "").toString();

    // Store the full text for the stop button
    setTypingFullText(finalText);

    // Mark that we're streaming
    isStreamingRef.current = true;
    
    // Remove thinking message and add empty assistant message
    setMessages((m) => {
      const withoutThinking = m.filter((msg) => msg.role !== "thinking");
      return [...withoutThinking, { role: "assistant", text: "" }];
    });

    // Set streaming state (keeps stop button visible)
    setUIState(prev => ({
      ...prev,
      isBusy: false,
      isStreamingUI: true
    }));

    // Typing animation constants
    const STEP = 5;  // characters per tick
    const TICK_MS = 10;  // ~100fps
    const RENDER_EVERY = 1;  // update DOM every tick

    let pos = 0;
    let tickCount = 0;

    const doTick = () => {
      if (!isStreamingRef.current) {
        // User hit stop - animation already halted
        return;
      }

      pos += STEP;
      tickCount++;

      const shouldRender = tickCount % RENDER_EVERY === 0 || pos >= finalText.length;

      if (shouldRender) {
        const chunk = finalText.slice(0, pos);
        setMessages((m) => {
          const copy = [...m];
          const last = copy[copy.length - 1];
          if (last && last.role === "assistant") {
            last.text = chunk;
          }
          return copy;
        });
        scrollToBottom(false);
      }

      if (pos >= finalText.length) {
        // Done typing
        isStreamingRef.current = false;
        setUIState({
          isBusy: false,
          isStreamingUI: false,
          typingFullText: ""
        });
        scrollToBottom(true);
        inputRef.current?.focus();
      } else {
        typingTimer.current = setTimeout(doTick, TICK_MS);
      }
    };

    doTick();
  };


  //
  // SEND MESSAGE
  //
  const send = async (forcedQuestion) => {
    const question = (forcedQuestion ?? input).trim();
    if (!question) return;

    // don't allow spamming while we're still answering last question
    if (isBusy || isStreamingRef.current) return;

    onPromptConsumed?.();

    // push the user's message
    setMessages((m) => [...m, { role: "user", text: question }]);

    // clear input instantly
    setInput("");

    // pin scroll and jump to bottom
    setIsPinned(true);
    scrollToBottom(true);

    // we're now waiting on backend - update state atomically
    setUIState({
      isBusy: true,
      isStreamingUI: false,
      typingFullText: ""
    });

    // show the "thinking..." placeholder bubble
    setMessages((m) => [...m, { role: "thinking", text: "thinking…" }]);

    try {
      const endpoint = `${(apiUrl || "/api/chat").replace(/\/$/, "")}`;
      console.log("[Atlas] endpoint ->", endpoint); // TEMP: verify once in console
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(apiKey ? { "X-Atlas-Key": apiKey } : {}),
        },
        // body: JSON.stringify({ question }),
        //  body: JSON.stringify({ q: question, k: 4, mode: "HYBRID" }),
          body: JSON.stringify({ question: question, k: 4, augment: true, session: "live-ui" }),

      });

      if (!res.ok) {
        beginStreaming(`Error: backend returned ${res.status}`);
        return;
      }

      const data = await res.json().catch(() => ({}));
      console.log("[AtlasUI] /query response:", data);

      // ---- NEW: derive meta + approximate flag (works for demo or router) ----
      // ---- derive meta + approximate flag (handles fallback/FAISS) ----
      const planMeta =
        (data && data.data && data.data.meta) ||
        (data && data.meta) ||
        {};

      const badges = Array.isArray(planMeta?.badges) ? planMeta.badges : [];
      const modeStr = (planMeta?.mode || "").toString();
      const warnStr = (planMeta?.warning || "").toString();
      const augDbg  = planMeta?.augment_debug || {};

      // Treat ANY fallback / vector path as approximate
      const isApprox =
       planMeta.approximate === true ||
       (Array.isArray(planMeta.badges) && planMeta.badges.includes("APPROXIMATE")) ||
       /fallback/i.test(planMeta.mode || "") ||
       /fallback/i.test(planMeta.warning || "") ||
       !!planMeta.rag_ctx_preview ||
      (Array.isArray(data?.rows) && data.rows.length === 0 && !!data?.context);


      const modeText = planMeta?.mode ? ` • Mode: ${planMeta.mode}` : "";
      const warnText = planMeta?.warning ? ` • ${planMeta.warning}` : "";
      const ragErr   = planMeta?.rag_error ? ` • rag_error: ${planMeta.rag_error}` : "";

      // ---- show a small badge bubble first ----
      // Keep "thinking" message so stop button remains visible until beginStreaming starts
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text:
            (isApprox
              ? "⚠️ Approximate: summarized from retrieved context."
              : "✅ Exact: computed from structured data (aggregate).") +
            modeText +
            warnText +
            ragErr,
        },
      ]);


      // update right-rail context (accept array or string)
      if (onContextUpdate) {
        const meta = (data && data.data && data.data.meta) || data?.meta || {};
        const debug = meta?.augment_debug || {};
        const lineage = Array.isArray(meta?.lineage)
          ? meta.lineage.map(
              (s, i) => `#${i + 1} ${s.op || "?"} @ ${s.source || ""} → rows=${s.rows_after_step ?? "?"}`
            )
          : [];

        // pull executor result (works for both top-level or nested responses)
        const rows =
          (Array.isArray(data?.rows) && data.rows) ||
          (Array.isArray(data?.data?.rows) && data.data.rows) ||
          [];

        // derive columns (prefer API-provided, else union of keys)
        const columns =
          (Array.isArray(data?.columns) && data.columns) ||
          (Array.isArray(data?.data?.columns) && data.data.columns) ||
          Array.from(
            rows.reduce((s, r) => {
              Object.keys(r || {}).forEach((k) => s.add(k));
              return s;
            }, new Set())
          );

        // reuse existing helper to render a compact markdown table
        const tableMd = rowsToMarkdownTable(rows, 25); // show first 25

        const ctxLines = [];
        ctxLines.push(`🧭 PLAN INTENT: ${meta.plan_intent || "?"}`);
        if (meta.mode) ctxLines.push(`⚙️  MODE: ${meta.mode}`);
        if (meta.badges?.length) ctxLines.push(`🏷️  BADGES: ${meta.badges.join(", ")}`);
        if (meta.warning) ctxLines.push(`⚠️  WARNING: ${meta.warning}`);
        ctxLines.push(`───────────────────────────────`);
        ctxLines.push(`context_rows: ${debug.context_rows ?? rows.length ?? 0}`);
        ctxLines.push(`columns_in_context: ${columns.slice(0, 40).join(", ")}`);
        ctxLines.push(`lineage_steps: ${debug.lineage_steps ?? (meta.lineage?.length || 0)}`);
        ctxLines.push(`vector_used: ${debug.vector_used ? "yes" : "no"}`);
        ctxLines.push(`mode: ${debug.mode || "rows→LLM"}`);
        if (lineage.length) {
          ctxLines.push(`───────────────────────────────`);
          ctxLines.push(`LINEAGE:`);
          ctxLines.push(lineage.join("\n"));
        }

        // 👇 add the actual executor output (compact)
        ctxLines.push(`───────────────────────────────`);
        ctxLines.push(
          `STRUCTURED RESULT (first ${Math.min(25, rows.length)} of ${rows.length} rows):`
        );
        ctxLines.push(tableMd);

        // If FAISS ran, include its preview too
        if (meta.rag_ctx_preview) {
          ctxLines.push(`───────────────────────────────`);
          ctxLines.push(`FAISS PREVIEW:`);
          ctxLines.push(meta.rag_ctx_preview);
        }

        onContextUpdate(ctxLines.join("\n"));
      }



      // // animate the MVP answer
      // beginStreaming(
      //   data.answer ||
      //     data.output ||
      //     data.message ||
      //     "(no answer from model)"
      // );
     // Prefer LLM narrative if present; else table; else note
     const rows = data?.rows || [];
      if (data?.answer) {
        beginStreaming(data.answer);
      } else if (rows.length > 0) {
        beginStreaming(rowsToMarkdownTable(rows));
      } else {
        beginStreaming(data?.output || data?.message || "(No rows.)");
      }

    } catch (err) {
      beginStreaming(`Error contacting backend: ${err.message}`);
    }
  };

  //
  // DERIVED UI FLAGS
  //
  const isThinkingVisible = messages.some((m) => m.role === "thinking");

  // Disable input any time Atlas is thinking OR streaming/animating
  const isInputDisabled = isThinkingVisible || isStreamingUI || isBusy;

  // Stop button should be visible whenever we're processing
  const showStop = isBusy || isStreamingUI || isThinkingVisible;

  //
  // RENDER
  //
  return (
    <div className={`flex flex-col w-full h-full min-h-0 flex-1 relative ${className}`}>
      {/* Status bar across the top of the chat area */}
      <div
        className={`h-[4px] w-full flex-shrink-0 transition-all duration-700 ${
          showStop
            ? "bg-[length:200%_200%] animate-gradient-move bg-gradient-to-r from-blue-500 via-cyan-400 to-teal-400"
            : "bg-gradient-to-r from-blue-500/20 via-cyan-400/20 to-teal-400/20"
        }`}
      />

      {/* Scrollable message history */}
      <div
        ref={chatScrollRef}
        className="flex-1 min-h-0 overflow-y-auto px-2 sm:px-4 text-slate-800 bg-gradient-to-b from-transparent to-white/40"
      >
        {messages.length === 0 && (
          <div className="mt-8 sm:mt-12 text-center text-xs sm:text-sm text-slate-500 px-4">
            Ask about a PO, SO, LPN, or item to get started.
          </div>
        )}
        {messages.map((m, i) => (
         <Message key={i + "-" + m.role.slice(0, 2)} role={m.role} text={m.text} />
        ))}

        {/* Mobile-only Sample Questions button - shows after each assistant response */}
        {!isInputDisabled && (
          <div className="sm:hidden flex justify-center py-4">
            <button
              onClick={() => setShowMobileDrawer(true)}
              className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg hover:brightness-110 active:scale-95 transition-all"
            >
              <span className="text-base">💡</span>
              <span>Sample Questions</span>
            </button>
          </div>
        )}
      </div>

      {/* Input row / footer */}
      <form
        className="flex-shrink-0 flex flex-col gap-2 rounded-b-2xl bg-white/80 backdrop-blur border-t border-white/60 px-2 sm:px-4 py-2 sm:py-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (!isInputDisabled) send();
        }}
      >
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full">
          {/* Text input */}
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Atlas..."
            disabled={isInputDisabled}
            className={
              "flex-1 rounded-xl border px-3 py-2 text-sm focus:outline-none transition-all duration-300 " +
              (isInputDisabled
                ? "bg-slate-100 text-slate-400 cursor-not-allowed border-slate-200"
                : justPrefilled
                ? "bg-white border-blue-400 ring-2 ring-blue-300/60 shadow-[0_0_10px_rgba(59,130,246,0.35)]"
                : "bg-white border-slate-300 focus:ring-2 focus:shadow-[0_0_8px_2px_rgba(56,189,248,0.4),0_0_16px_4px_rgba(45,212,191,0.2)] focus:ring-blue-400/40")
            }
          />

          {/* Buttons on the right (stack on mobile) */}
          <div className="flex items-center gap-2">
            {/* Ask Atlas button */}
            <button
              type="submit"
              disabled={isInputDisabled}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-white shadow-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 hover:brightness-110 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              <img
                src="/logos/atlas-mark-dark-bg.png"
                alt="Atlas Logo"
                className="h-4 w-4 object-contain filter brightness-0 invert opacity-90"
              />
              <span className="hidden sm:inline">Ask Atlas</span>
              <span className="sm:hidden">Ask</span>
            </button>

            {/* Stop button */}
            {showStop && (
              <button
                type="button"
                onClick={stopTyping}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1 rounded-full border border-slate-300 bg-white/90 px-3 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 active:bg-slate-100 ring-1 ring-slate-200 whitespace-nowrap"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className="h-4 w-4"
                >
                  <rect x="6" y="6" width="8" height="8" rx="1.5" />
                </svg>
                <span>Stop</span>
              </button>
            )}
          </div>
        </div>

        {/* Mobile-only Data Sources button - below Ask button */}
        {onOpenDataSources && (
          <div className="xl:hidden flex justify-center">
            <button
              type="button"
              onClick={onOpenDataSources}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white/90 px-3 py-2 text-xs font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:border-slate-300 active:bg-slate-100 transition-all"
              title="View Data Sources"
              aria-label="View Data Sources"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-slate-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
                />
              </svg>
              <span>Data used for this Demo</span>
            </button>
          </div>
        )}
      </form>

      {/* Mobile Prompt Drawer */}
      <MobilePromptDrawer
        isOpen={showMobileDrawer}
        onClose={() => setShowMobileDrawer(false)}
        onSelectPrompt={(prompt) => {
          // Auto-send the selected prompt
          send(prompt);
        }}
      />
    </div>
  );
}
