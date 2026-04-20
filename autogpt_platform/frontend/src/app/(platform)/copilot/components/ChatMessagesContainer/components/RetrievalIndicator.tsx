import { Button } from "@/components/atoms/Button/Button";
import { ScaleLoader } from "../../ScaleLoader/ScaleLoader";

interface Props {
  /** Whether the retrieval timeout has fired — switches copy + tone to error. */
  failed?: boolean;
}

function handleReload() {
  // Full reload rather than router.refresh(): the local useChat/Zustand
  // state is what's wedged, and a soft refresh leaves them intact.
  if (typeof window !== "undefined") window.location.reload();
}

/**
 * Replaces the generic "Thinking…" bubble when the user switches to a chat
 * whose backend stream is still active and the client is fetching the
 * replay. Distinct from the thinking state because the model isn't actually
 * deliberating; the wait is just network latency. After the retrieval
 * timeout expires the same slot flips to a destructive-toned inline
 * error with a reload button that forces the user out of the wedged
 * client state.
 */
export function RetrievalIndicator({ failed }: Props) {
  if (failed) {
    return (
      <span
        role="alert"
        className="inline-flex flex-wrap items-center gap-2 text-red-600"
      >
        <span>Failed to retrieve latest conversation.</span>
        <Button variant="destructive" size="small" onClick={handleReload}>
          Reload the page
        </Button>
      </span>
    );
  }
  return (
    <span
      role="status"
      aria-live="polite"
      className="inline-flex items-center gap-1.5 text-neutral-500"
    >
      <ScaleLoader size={16} />
      <span className="animate-pulse [animation-duration:1.5s]">
        Retrieving your conversation…
      </span>
    </span>
  );
}
