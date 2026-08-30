import type { ChatRequestResponse } from "../types/chat";
const API_BASE_URL = "http://localhost:5000/api";

export async function checkApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("API is unavailable");
  }

  return response.json();
}

export async function createChatRequest(message: string):Promise<ChatRequestResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Unable to send message");
  }

  return data;
}