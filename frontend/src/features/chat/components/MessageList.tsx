import { useEffect, useRef } from "react";
import type { ChatMessage } from "../types";

interface Props {
  messages: ChatMessage[];
  pending: boolean;
}

export function MessageList({ messages, pending }: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, pending]);

  return (
    <div className="chat__messages" aria-live="polite">
      {messages.map((m) => (
        <div key={m.id} className={`bubble bubble--${m.role}`}>
          {m.content}
        </div>
      ))}
      {pending && <div className="bubble bubble--assistant bubble--typing">…</div>}
      <div ref={endRef} />
    </div>
  );
}
