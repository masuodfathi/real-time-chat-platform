import DynamicRenderer from "./DynamicRenderer";

import type { ChatMessage } from "../types/chat";


interface MessageBubbleProps {
  message: ChatMessage;
}


function MessageBubble({
  message,
}: MessageBubbleProps) {
  return (
    <div
      className={`message ${message.role}`}
    >
      <strong>
        {message.role === "user"
          ? "You"
          : "Assistant"}
      </strong>

      <p>{message.content}</p>

      {message.components.map((component) => (
        <DynamicRenderer
          key={component.id}
          component={component}
        />
      ))}
    </div>
  );
}


export default MessageBubble;