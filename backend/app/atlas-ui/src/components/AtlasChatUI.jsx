import React, { useEffect, useRef, useState } from "react";
<Chip key={s} label={s} onClick={send} />
))}
</div >


    <div className="grid h-full grid-cols-1 gap-4 md:grid-cols-3">
        {/* Chat column */}
        <div className="col-span-2 flex flex-col rounded-2xl border border-zinc-200 bg-zinc-50 p-3">
            <div className="flex-1 overflow-y-auto p-1">
                {messages.length === 0 && (
                    <div className="mt-12 text-center text-sm text-zinc-500">
                        Ask about a PO, SO, LPN, or item to get started.
                    </div>
                )}
                {messages.map((m, i) => (
                    <Message key={i} role={m.role} text={m.text} />
                ))}
                {(loading || isTyping) && (
                    <div className="mt-1 text-center text-xs text-zinc-400">
                        {isTyping ? "typing…" : "thinking…"}
                    </div>
                )}
                <div ref={bottomRef} />
            </div>


            <div className="mb-2 flex items-center gap-3 text-xs text-zinc-600">
                <div className="flex items-center gap-2">
                    <span>Typing speed</span>
                    <input
                        type="range" min={1} max={40} value={typingSpeed}
                        onChange={(e) => setTypingSpeed(parseInt(e.target.value, 10))}
                    />
                    <span>{typingSpeed} ms/char</span>
                </div>
                {isTyping && (
                    <button
                        onClick={() => skipTypewriter(messages[messages.length - 1]?.text ?? "")}
                        className="rounded-md border border-zinc-300 px-2 py-1 hover:bg-zinc-100"
                    >
                        Skip to end
                    </button>
                )}
            </div>


            <form
                onSubmit={(e) => { e.preventDefault(); send(input); }}
                className="mt-1 flex items-center gap-2"
            >
                <input
                    placeholder="Ask Atlas about an order, item, or delivery…"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="flex-1 rounded-xl border border-zinc-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    type="submit"
                    disabled={loading || isTyping}
                    className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-blue-700 disabled:opacity-50"
                >
                    Send
                </button>
            </form>
        </div>


        {/* Context column */}
        <div className="flex flex-col rounded-2xl border border-zinc-200 bg-white p-3">
            <div className="mb-2 text-sm font-semibold">Retrieved context</div>
            <pre className="flex-1 overflow-auto whitespace-pre-wrap rounded-xl bg-zinc-50 p-3 text-xs text-zinc-700">
                {context || "(Empty — ask a question to see what Atlas retrieved)"}
            </pre>
            <div className="mt-2 text-[11px] text-zinc-500">
                Tip: Toggle <span className="font-semibold">Preview</span> to fetch context without generating an answer.
            </div>
        </div>
    </div>
</div >
);
}