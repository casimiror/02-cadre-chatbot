import { useEffect, useRef } from "react";
import type { ChatMessage } from "../types";
import { MessageContent } from "./MessageContent";

interface Props {
  messages: ChatMessage[];
  pending: boolean;
}

export function MessageList({ messages, pending }: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  // Braces matter: newer Chrome returns a Promise from scrollIntoView, and an effect must not
  // return anything but a cleanup function (React would call the Promise and crash).
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  return (
    <div className="chat__messages" aria-live="polite">
      {messages.map((m) => (
        <div key={m.id} className={`bubble bubble--${m.role}`}>
          <MessageContent role={m.role} content={m.content} />
        </div>
      ))}
      {pending && <div className="bubble bubble--assistant bubble--typing">…</div>}
      <div ref={endRef} />
    </div>
  );
}
