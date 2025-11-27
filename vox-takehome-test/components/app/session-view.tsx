'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { ProviderDetailsPanel } from '@/components/app/provider-details-panel';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}
interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: false,
    camera: false,
    screenShare: false,
  };

  useEffect(() => {
    const lastMessage = messages.at(-1);
    if (scrollAreaRef.current && lastMessage) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="bg-background relative z-10 flex h-screen w-full flex-col overflow-hidden" {...props}>
      <div className="border-input border-b bg-background fixed top-0 left-0 right-0 z-30 flex h-16 items-center justify-center">
        <h1 className="text-foreground text-xl font-semibold">Healthcare Assistant</h1>
      </div>

      <div className="relative z-20 flex h-[calc(100vh-120px)] md:h-[calc(100vh-160px)] overflow-hidden pt-16">
        <div className="border-input flex w-1/2 flex-col border-r overflow-hidden bg-background">
          <div className="border-input border-b bg-background flex-shrink-0 p-4">
            <h2 className="text-foreground text-lg font-semibold">Conversation</h2>
          </div>
          <ScrollArea ref={scrollAreaRef} className="flex-1 min-h-0 bg-background p-4">
            <ChatTranscript
              hidden={false}
              messages={messages}
              className="space-y-3"
            />
          </ScrollArea>
        </div>

        <div className="flex w-1/2 flex-col overflow-hidden bg-background">
          <ProviderDetailsPanel />
        </div>
      </div>
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar controls={controls} />
        </div>
      </MotionBottom>
    </section>
  );
};
