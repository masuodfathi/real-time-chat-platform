import { useState } from "react";

import {
  createChatRequest,
  openChatStream,
} from "./services/chatApi";

import MessageList from "./components/MessageList";

import type {
  ChatMessage,
  ChatStreamEvent,
} from "./types/chat";


function App() {
  const [input, setInput] = useState("");

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [error, setError] = useState("");

  const [isSending, setIsSending] =
    useState(false);


  async function handleSubmit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    const trimmedMessage = input.trim();

    if (!trimmedMessage) {
      setError("Please enter a message.");
      return;
    }

    setError("");
    setIsSending(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedMessage,
      components: [],
    };

    const assistantMessageId =
      crypto.randomUUID();

    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      components: [],
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
      assistantMessage,
    ]);

    setInput("");

    try {
      const result =
        await createChatRequest(trimmedMessage);

      openChatStream(
        result.requestId,

        (streamEvent) =>
          handleStreamEvent(
            assistantMessageId,
            streamEvent
          ),

        (message) => {
          setError(message);
          setIsSending(false);
        }
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }

      setIsSending(false);
    }
  }


  function handleStreamEvent(
    assistantMessageId: string,
    event: ChatStreamEvent
  ) {
    if (event.type === "message.delta") {
      setMessages((currentMessages) =>
        currentMessages.map((message) => {
          if (
            message.id !== assistantMessageId
          ) {
            return message;
          }

          return {
            ...message,
            content:
              message.content +
              event.data.text,
          };
        })
      );
    }

    if (event.type === "ui.component") {
      setMessages((currentMessages) =>
        currentMessages.map((message) => {
          if (
            message.id !== assistantMessageId
          ) {
            return message;
          }

          return {
            ...message,
            components: [
              ...message.components,
              event.data,
            ],
          };
        })
      );
    }

    if (event.type === "message.done") {
      setIsSending(false);
    }

    if (event.type === "error") {
      setError(event.data.message);
      setIsSending(false);
    }
  }


  return (
    <main>
      <h1>Real-Time Chat Platform</h1>

      <MessageList messages={messages} />

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Type a message..."
        />

        <button
          type="submit"
          disabled={isSending}
        >
          {isSending
            ? "Responding..."
            : "Send"}
        </button>
      </form>

      {error && <p>{error}</p>}
    </main>
  );
}


export default App;