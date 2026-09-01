import MessageBubble from "./MessageBubble";

import type { ChatMessage } from "../types/chat";


interface MessageListProps {
  messages: ChatMessage[];
}


function MessageList({
  messages,
}: MessageListProps) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}


export default MessageList;