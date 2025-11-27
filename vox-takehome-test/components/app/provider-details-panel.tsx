'use client';

import * as React from 'react';
import { useEffect } from 'react';
import { useProviderData } from '@/hooks/useProviderData';
import { ProviderList } from '@/components/app/provider-card';
import { ScrollArea } from '@/components/livekit/scroll-area/scroll-area';
import { cn } from '@/lib/utils';

interface ProviderDetailsPanelProps {
  className?: string;
}

export function ProviderDetailsPanel({ className }: ProviderDetailsPanelProps) {
  const { providers } = useProviderData();
  
  // Only log when providers actually change, not on every render
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('ProviderDetailsPanel - providers:', providers.length, providers.map(p => ({ id: p.id, name: p.full_name })));
    }
  }, [providers]);

  if (providers.length === 0) {
    return (
      <div
        className={cn(
          'bg-muted/30 border-input flex h-full flex-col items-center justify-center overflow-hidden p-8',
          className
        )}
      >
        <div className="text-muted-foreground text-center">
          <p className="text-lg font-medium">Provider Details</p>
          <p className="mt-2 text-sm">
            Provider information will appear here when the agent finds providers.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-background border-input flex h-full flex-col overflow-hidden',
        className
      )}
    >
      <div className="border-input border-b bg-background flex-shrink-0 p-4">
        <h2 className="text-foreground text-lg font-semibold">Provider Details</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          {providers.length} {providers.length === 1 ? 'provider' : 'providers'} found
        </p>
      </div>
      <ScrollArea className="flex-1 bg-background p-4">
        <ProviderList providers={providers} />
      </ScrollArea>
    </div>
  );
}

