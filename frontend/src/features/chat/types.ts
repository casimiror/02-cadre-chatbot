export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
}

// Mirrors backend app/schemas/chat.py
export interface ChatRequest {
  conversation_id: string | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  reply: string;
}
