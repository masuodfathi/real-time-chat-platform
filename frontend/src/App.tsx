import { useEffect, useState } from "react";
import { checkApiHealth } from "./services/chatApi";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    checkApiHealth()
      .then(() => {
        setStatus("Backend connected");
      })
      .catch(() => {
        setStatus("Backend connection failed");
      });
  }, []);

  return (
    <main>
      <h1>Real-Time Chat Platform</h1>

      <p>{status}</p>
    </main>
  );
}

export default App;