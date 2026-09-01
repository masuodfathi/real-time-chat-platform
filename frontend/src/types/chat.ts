export interface ChatRequestResponse {
  requestId: string;
}

export type ServerUIComponent =
  | {
      id: string;
      type: "info_card";
      props: {
        title: string;
        description: string;
        rating?: number;
      };
    }
  | {
      id: string;
      type: "quick_replies";
      props: {
        options: string[];
      };
    };

export type ChatStreamEvent =
  | {
      type: "message.delta";
      data: {
        text: string;
      };
    }
  | {
      type: "ui.component";
      data: ServerUIComponent;
    }
  | {
      type: "message.done";
    }
  | {
      type: "error";
      data: {
        message: string;
      };
    };

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  components: ServerUIComponent[];
}