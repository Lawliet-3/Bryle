"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Source = { index: number; title: string; url: string; snippet: string };
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};
type StreamEvent =
  | { type: "sources"; sources: Source[] }
  | { type: "delta"; text: string }
  | { type: "error"; message: string }
  | { type: "done" };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const suggestions = [
  "What is this website about?",
  "Summarize the most important information.",
  "What should a new visitor know first?",
];

function ArrowIcon() {
  return <span aria-hidden="true">↗</span>;
}

function SourceCards({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;
  return (
    <div className="sources" aria-label="Sources used">
      {sources.map((source) => (
        <a href={source.url} target="_blank" rel="noreferrer" className="source-card" key={source.url}>
          <span className="source-number">{source.index}</span>
          <span className="source-copy">
            <strong>{source.title}</strong>
            <small>{source.snippet}</small>
          </span>
          <ArrowIcon />
        </a>
      ))}
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState("Connecting…");
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(async (response) => {
        if (!response.ok) throw new Error();
        return response.json();
      })
      .then((data) => setStatus(`${data.indexed_chunks} passages ready`))
      .catch(() => setStatus("Backend setup required"));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ask(rawQuestion: string) {
    const trimmed = rawQuestion.trim();
    if (!trimmed || isStreaming) return;

    const previousMessages = messages;
    const userMessage: Message = { id: crypto.randomUUID(), role: "user", content: trimmed };
    const assistantId = crypto.randomUUID();
    setMessages([...previousMessages, userMessage, { id: assistantId, role: "assistant", content: "", sources: [] }]);
    setQuestion("");
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          question: trimmed,
          history: previousMessages.map(({ role, content }) => ({ role, content })),
        }),
      });
      if (!response.ok || !response.body) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? "The assistant is unavailable.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
        const frames = buffer.split("\n\n");
        buffer = frames.pop() ?? "";

        for (const frame of frames) {
          const dataLine = frame.split("\n").find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const event = JSON.parse(dataLine.slice(6)) as StreamEvent;
          setMessages((current) =>
            current.map((message) => {
              if (message.id !== assistantId) return message;
              if (event.type === "sources") return { ...message, sources: event.sources };
              if (event.type === "delta") return { ...message, content: message.content + event.text };
              if (event.type === "error") return { ...message, content: event.message };
              return message;
            }),
          );
        }
        if (done) break;
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        const errorMessage =
          error instanceof TypeError
            ? "The backend is unavailable. Start the API and try again."
            : (error as Error).message || "Something went wrong. Please try again.";
        setMessages((current) =>
          current.map((item) =>
            item.id === assistantId
              ? { ...item, content: errorMessage }
              : item,
          ),
        );
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  return (
    <main>
      <header className="topbar">
        <a href="#" className="brand" aria-label="Bryle home">
          <span className="brand-mark">B</span>
          <span>Bryle</span>
        </a>
        <div className="status"><i />{status}</div>
      </header>

      <section className={`conversation ${messages.length ? "has-messages" : ""}`}>
        {!messages.length && (
          <div className="hero">
            <span className="eyebrow">Website intelligence, with receipts</span>
            <h1>Ask the site.<br /><em>Get the source.</em></h1>
            <p>Bryle retrieves the most relevant passages, then answers with links you can inspect.</p>
            <div className="suggestions">
              {suggestions.map((suggestion) => (
                <button key={suggestion} onClick={() => void ask(suggestion)}>{suggestion}<ArrowIcon /></button>
              ))}
            </div>
          </div>
        )}

        <div className="messages" aria-live="polite">
          {messages.map((message) => (
            <article className={`message ${message.role}`} key={message.id}>
              <span className="message-label">{message.role === "user" ? "You" : "Bryle"}</span>
              <div className="message-content">
                {message.content || (isStreaming && message.role === "assistant" ? <span className="thinking">Thinking</span> : null)}
              </div>
              {message.role === "assistant" && message.sources && <SourceCards sources={message.sources} />}
            </article>
          ))}
          <div ref={endRef} />
        </div>
      </section>

      <footer className="composer-wrap">
        <form className="composer" onSubmit={submit}>
          <textarea
            aria-label="Ask Bryle"
            placeholder="Ask a question about the indexed website…"
            value={question}
            rows={1}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          {isStreaming ? (
            <button type="button" className="send stop" onClick={() => abortRef.current?.abort()} aria-label="Stop response">■</button>
          ) : (
            <button type="submit" className="send" disabled={!question.trim()} aria-label="Send question">↑</button>
          )}
        </form>
        <small>Answers are generated from retrieved content. Verify important details in the sources.</small>
      </footer>
    </main>
  );
}
