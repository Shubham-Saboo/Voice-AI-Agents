import { useEffect, useState, useCallback, useRef } from 'react';
import { Room, TextStreamReader } from 'livekit-client';
import { useRoomContext } from '@livekit/components-react';
import type { Provider } from '@/components/app/provider-card';

export interface ProviderData {
  type: 'provider_data';
  data: {
    providers?: Provider[];
    provider?: Provider;
    count?: number;
    found?: boolean;
  };
  timestamp: number;
}

export function useProviderData() {
  const room = useRoomContext();
  const [providers, setProviders] = useState<Provider[]>([]);
  const handlerRegisteredRef = useRef(false);
  const roomRef = useRef<Room | null>(null);

  useEffect(() => {
    if (!room) {
      roomRef.current = null;
      return;
    }

    // Track room instance to detect changes
    const isNewRoom = roomRef.current !== room;
    roomRef.current = room;

    const handleProviderData = async (reader: TextStreamReader, participantIdentity: string) => {
      console.log('🎯 Handler called! Received text stream from:', participantIdentity);
      try {
        const message = await reader.readAll();
        console.log('📨 Raw message received (length):', message.length, 'chars');
        const data: ProviderData = JSON.parse(message);
        
        console.log('📥 Parsed provider data:', {
          type: data.type,
          timestamp: data.timestamp,
          hasProviders: !!data.data.providers,
          hasProvider: !!data.data.provider,
          providerCount: data.data.providers?.length || (data.data.provider ? 1 : 0),
          data: data.data
        });
        
        if (data.type === 'provider_data') {
          const newProviders: Provider[] = [];
          
          if (data.data.providers && Array.isArray(data.data.providers)) {
            newProviders.push(...data.data.providers);
          }
          
          if (data.data.provider) {
            newProviders.push(data.data.provider);
          }
          
          if (newProviders.length > 0) {
            console.log('✅ Extracted providers:', newProviders.length, newProviders.map(p => ({ id: p.id, name: p.full_name })));
            setProviders((prev) => {
              const providerMap = new Map<number, Provider>();
              prev.forEach(p => providerMap.set(p.id, p));
              newProviders.forEach(p => {
                if (p.id) {
                  providerMap.set(p.id, p);
                }
              });
              return Array.from(providerMap.values());
            });
          }
        }
      } catch (error) {
        console.error('❌ Error parsing provider data:', error);
      }
    };

    const registerHandler = () => {
      // Reset flag if room changed
      if (isNewRoom) {
        handlerRegisteredRef.current = false;
      }
      
      if (handlerRegisteredRef.current) {
        console.log('⚠️ Handler already registered, skipping');
        return;
      }
      
      try {
        // Register handler immediately - LiveKit can queue handlers even before connection
        room.registerTextStreamHandler('lk.provider_data', handleProviderData);
        handlerRegisteredRef.current = true;
        console.log('✅ Registered text stream handler for lk.provider_data on room:', room.name, 'state:', room.state);
      } catch (error) {
        if (error instanceof Error && error.message.includes('already been set')) {
          handlerRegisteredRef.current = true;
          console.log('✅ Handler already registered for lk.provider_data');
        } else {
          console.error('❌ Error registering text stream handler:', error);
          // Try again on next state change if registration failed
          handlerRegisteredRef.current = false;
        }
      }
    };

    // Register handler immediately regardless of connection state
    // LiveKit can queue handlers even before the room is fully connected
    registerHandler();

    // Also set up listener for state changes to re-register if needed
    const handleStateChange = () => {
      console.log('🔄 Room state changed to:', room.state);
      if (room.state === 'connected' && !handlerRegisteredRef.current) {
        console.log('🔄 Re-registering handler after connection');
        registerHandler();
      }
    };
    
    room.on('stateChanged', handleStateChange);
    
    return () => {
      room.off('stateChanged', handleStateChange);
      if (isNewRoom) {
        handlerRegisteredRef.current = false;
        setProviders([]);
      }
    };

    // Cleanup: reset flag when room changes
    return () => {
      if (isNewRoom) {
        handlerRegisteredRef.current = false;
        setProviders([]);
      }
    };
  }, [room]);

  const clearProviders = useCallback(() => {
    setProviders([]);
  }, []);

  return {
    providers,
    clearProviders,
  };
}

