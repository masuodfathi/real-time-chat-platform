import { useState } from "react";
import { createChatRequest } from "./services/chatApi";

function App() {
  const [message, setMessage] = useState("");
  const [requestId, setRequestId] = useState("");
  const [error, setError] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    setError("");
    setRequestId("");

    if (!message.trim()) {
      setError("Please enter a message.");
      return;
    }

    try {
      setIsSending(true);

      const result = await createChatRequest(message);

      setRequestId(result.requestId);

      setMessage("");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main>
      <h1>Real-Time Chat Platform</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Type a message..."
        />

        <button type="submit" disabled={isSending}>
          {isSending ? "Sending..." : "Send"}
        </button>
      </form>

      {requestId && (
        <p>
          Request ID: <strong>{requestId}</strong>
        </p>
      )}

      {error && <p>{error}</p>}
    </main>
  );
}

export default App;