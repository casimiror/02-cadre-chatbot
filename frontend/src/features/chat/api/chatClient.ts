import type { ChatRequest, ChatResponse } from "../types";

export class ChatApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

// The only place that knows the HTTP contract.
export async function sendMessage(body: ChatRequest): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 429) {
    throw new ChatApiError("You're sending messages too fast. Wait a moment and try again.", 429);
  }
  if (!res.ok) {
    throw new ChatApiError("Something went wrong on our side. Please try again.", res.status);
  }
  return res.json();
}
