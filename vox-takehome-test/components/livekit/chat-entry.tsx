import * as React from 'react';
import { cn } from '@/lib/utils';
import type { Provider } from '@/components/app/provider-card';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
  /** Provider data to display with the message. */
  providers?: Provider[];
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  providers,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });
  const hasProviders = providers && providers.length > 0;

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn('group flex w-full flex-col gap-2', className)}
      {...props}
    >
      <div className={cn('flex w-full flex-col gap-0.5', messageOrigin === 'local' && 'items-end')}>
        <header
          className={cn(
            'text-muted-foreground flex items-center gap-2 text-sm',
            messageOrigin === 'local' ? 'flex-row-reverse' : 'text-left'
          )}
        >
          {name && <strong>{name}</strong>}
          <span className="font-mono text-xs opacity-0 transition-opacity ease-linear group-hover:opacity-100">
            {hasBeenEdited && '*'}
            {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
          </span>
        </header>
        <span
          className={cn(
            'max-w-4/5 rounded-[20px]',
            messageOrigin === 'local' ? 'bg-muted ml-auto p-2' : 'mr-auto'
          )}
        >
          {message}
        </span>
      </div>
      {/* Provider cards are now shown in the right panel, not inline */}
    </li>
  );
};
