import { useMemo } from 'react';
import { Room } from 'livekit-client';
import {
  type ReceivedChatMessage,
  type TextStreamData,
  useChat,
  useRoomContext,
  useTranscriptions,
} from '@livekit/components-react';
import type { Provider } from '@/components/app/provider-card';

export interface ExtendedChatMessage extends ReceivedChatMessage {
  providers?: Provider[];
}

function transcriptionToChatMessage(textStream: TextStreamData, room: Room): ReceivedChatMessage {
  return {
    id: textStream.streamInfo.id,
    timestamp: textStream.streamInfo.timestamp,
    message: textStream.text,
    from:
      textStream.participantInfo.identity === room.localParticipant.identity
        ? room.localParticipant
        : Array.from(room.remoteParticipants.values()).find(
            (p) => p.identity === textStream.participantInfo.identity
          ),
  };
}

export function useChatMessages() {
  const chat = useChat();
  const room = useRoomContext();
  const transcriptions: TextStreamData[] = useTranscriptions();

  const mergedTranscriptions = useMemo(() => {
    const transcriptionMessages = transcriptions.map((transcription) => 
      transcriptionToChatMessage(transcription, room)
    );
    
    const allMessages = [...transcriptionMessages, ...chat.chatMessages];
    const messageMap = new Map<string, ExtendedChatMessage>();
    
    for (const message of allMessages) {
      const existing = messageMap.get(message.id);
      if (!existing || 
          message.timestamp > existing.timestamp ||
          (message.timestamp === existing.timestamp && message.message.length > existing.message.length)) {
        messageMap.set(message.id, message);
      }
    }
    
    return Array.from(messageMap.values()).sort((a, b) => {
      if (a.timestamp !== b.timestamp) {
        return a.timestamp - b.timestamp;
      }
      return a.id.localeCompare(b.id);
    });
  }, [transcriptions, chat.chatMessages, room]);

  return mergedTranscriptions;
}
