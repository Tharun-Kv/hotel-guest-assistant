import { useCallback, useMemo, useState } from 'react';

import { ApiError, checkAvailability, sendChatMessage } from '@/lib/api';
import type { AvailabilityResult } from '@/types/availability';
import type { ChatMessage, ChatProgressStep, ConversationEntry } from '@/types/chat';

type RetryAction = (() => Promise<void>) | null;

const WELCOME_MESSAGE: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content: 'Welcome to Harbor View Hotel. I can help with hotel details, room recommendations, and availability.',
};

const MINIMUM_RESPONSE_DELAY_MS = 3_000;
const PROGRESS_TIMINGS = [900, 1_950] as const;

function wait(milliseconds: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, milliseconds));
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [availabilityState, setAvailabilityState] = useState<AvailabilityResult | null>(null);
  const [retryAction, setRetryAction] = useState<RetryAction>(null);
  const [progressStep, setProgressStep] = useState<ChatProgressStep | null>(null);

  const conversation = useMemo<ConversationEntry[]>(
    () => messages.filter((message) => message.id !== WELCOME_MESSAGE.id).map(({ role, content }) => ({ role, content })),
    [messages],
  );

  const showError = useCallback((err: unknown) => {
    setError(err instanceof ApiError || err instanceof Error ? err.message : 'Something went wrong. Please try again.');
  }, []);

  const postMessage = useCallback(async (input: string, addOptimisticMessage: boolean) => {
    const message = input.trim();
    if (!message || loading) return;
    setLoading(true);
    setError(null);
    setProgressStep('connecting');
    const progressTimers = [
      setTimeout(() => setProgressStep('checking'), PROGRESS_TIMINGS[0]),
      setTimeout(() => setProgressStep('preparing'), PROGRESS_TIMINGS[1]),
    ];
    if (addOptimisticMessage) {
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'user', content: message }]);
    }

    try {
      const responsePromise = sendChatMessage(message, conversationId, conversation);
      const [response] = await Promise.all([responsePromise, wait(MINIMUM_RESPONSE_DELAY_MS)]);
      setConversationId(response.conversation_id);
      setMessages((current) => [...current, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.message,
        responseType: response.type,
        sources: response.sources,
      }]);
      if (response.availability) setAvailabilityState(response.availability);
      setRetryAction(null);
    } catch (err) {
      showError(err);
      setRetryAction(() => () => postMessage(message, false));
    } finally {
      progressTimers.forEach((timer) => clearTimeout(timer));
      setProgressStep(null);
      setLoading(false);
    }
  }, [conversation, conversationId, loading, showError]);

  const sendMessage = useCallback((input: string) => postMessage(input, true), [postMessage]);

  const checkRoomAvailability = useCallback(async (checkIn: string, checkOut: string, adults: number) => {
    if (loading) return;
    setLoading(true);
    setError(null);
    setProgressStep('connecting');
    const progressTimers = [
      setTimeout(() => setProgressStep('checking'), PROGRESS_TIMINGS[0]),
      setTimeout(() => setProgressStep('preparing'), PROGRESS_TIMINGS[1]),
    ];
    try {
      const availabilityPromise = checkAvailability(checkIn, checkOut, adults);
      const [result] = await Promise.all([availabilityPromise, wait(MINIMUM_RESPONSE_DELAY_MS)]);
      setAvailabilityState(result);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: result.available
            ? `I found ${result.rooms.length} room option(s) for ${adults} guests from ${checkIn} to ${checkOut}.`
            : 'No rooms match that date range and guest count.',
        },
      ]);
      setRetryAction(null);
    } catch (err) {
      showError(err);
      setRetryAction(() => () => checkRoomAvailability(checkIn, checkOut, adults));
    } finally {
      progressTimers.forEach((timer) => clearTimeout(timer));
      setProgressStep(null);
      setLoading(false);
    }
  }, [loading, showError]);

  const retry = useCallback(() => retryAction?.(), [retryAction]);

  const resetConversation = useCallback(() => {
    if (loading) return;
    setMessages([WELCOME_MESSAGE]);
    setConversationId(null);
    setAvailabilityState(null);
    setError(null);
    setRetryAction(null);
    setProgressStep(null);
  }, [loading]);

  return {
    messages,
    loading,
    error,
    conversationId,
    availabilityState,
    sendMessage,
    checkRoomAvailability,
    retry,
    resetConversation,
    progressStep,
    clearError: () => setError(null),
  };
}
