import { SSEEvent } from "./types";

type EventHandler = (event: SSEEvent) => void;

export function createSSEConnection(url: string, onEvent: EventHandler): () => void {
  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as SSEEvent;
      onEvent(data);
    } catch {
      // ignore parse errors on incomplete chunks
    }
  };

  eventSource.onerror = () => {
    onEvent({ type: "error", message: "Connection lost. Retrying..." });
  };

  return () => eventSource.close();
}
