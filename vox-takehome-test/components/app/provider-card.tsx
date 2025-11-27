'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface Provider {
  id: number;
  full_name: string;
  first_name?: string;
  last_name?: string;
  specialty: string;
  phone?: string;
  email?: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
  };
  years_experience?: number;
  accepting_new_patients?: boolean;
  insurance_accepted?: string[];
  rating?: number;
  license_number?: string;
  board_certified?: boolean;
  languages?: string[];
}

interface ProviderCardProps {
  provider: Provider;
  className?: string;
}

export function ProviderCard({ provider, className }: ProviderCardProps) {
  const formatAddress = () => {
    if (!provider.address) return null;
    const parts = [
      provider.address.street,
      provider.address.city,
      provider.address.state,
      provider.address.zip,
    ].filter(Boolean);
    return parts.length > 0 ? parts.join(', ') : null;
  };

  const formatInsurance = () => {
    if (!provider.insurance_accepted || provider.insurance_accepted.length === 0) {
      return 'Not specified';
    }
    if (provider.insurance_accepted.length <= 3) {
      return provider.insurance_accepted.join(', ');
    }
    return `${provider.insurance_accepted.slice(0, 3).join(', ')} and ${provider.insurance_accepted.length - 3} more`;
  };

  const formatLanguages = () => {
    if (!provider.languages || provider.languages.length === 0) {
      return 'English';
    }
    return provider.languages.join(', ');
  };

  return (
    <div
      className={cn(
        'bg-muted/50 border-input rounded-lg border p-4 space-y-3',
        className
      )}
    >
      {/* Header */}
      <div className="space-y-1">
        <h3 className="text-foreground font-semibold text-base">{provider.full_name}</h3>
        {provider.specialty && (
          <p className="text-muted-foreground text-sm">{provider.specialty}</p>
        )}
      </div>

      {/* Rating and Status */}
      <div className="flex items-center gap-4 text-sm">
        {provider.rating !== undefined && (
          <div className="text-foreground flex items-center gap-1">
            <span className="font-medium">{provider.rating.toFixed(1)}</span>
            <span className="text-muted-foreground">★</span>
          </div>
        )}
        {provider.board_certified && (
          <span className="text-muted-foreground text-xs">Board Certified</span>
        )}
        {provider.accepting_new_patients !== undefined && (
          <span
            className={cn(
              'text-xs',
              provider.accepting_new_patients
                ? 'text-green-600 dark:text-green-400'
                : 'text-muted-foreground'
            )}
          >
            {provider.accepting_new_patients ? 'Accepting Patients' : 'Not Accepting'}
          </span>
        )}
      </div>

      {/* Contact Information */}
      <div className="space-y-2 text-sm">
        {formatAddress() && (
          <div className="text-muted-foreground flex items-start gap-2">
            <span className="text-xs">📍</span>
            <span>{formatAddress()}</span>
          </div>
        )}
        {provider.phone && (
          <div className="text-muted-foreground flex items-center gap-2">
            <span className="text-xs">📞</span>
            <a href={`tel:${provider.phone}`} className="hover:text-foreground underline">
              {provider.phone}
            </a>
          </div>
        )}
        {provider.email && (
          <div className="text-muted-foreground flex items-center gap-2">
            <span className="text-xs">✉️</span>
            <a href={`mailto:${provider.email}`} className="hover:text-foreground underline">
              {provider.email}
            </a>
          </div>
        )}
      </div>

      {/* Additional Details */}
      <div className="space-y-2 text-xs text-muted-foreground border-t pt-2">
        {provider.years_experience !== undefined && (
          <div>
            <span className="font-medium">Experience:</span> {provider.years_experience} years
          </div>
        )}
        <div>
          <span className="font-medium">Languages:</span> {formatLanguages()}
        </div>
        <div>
          <span className="font-medium">Insurance:</span> {formatInsurance()}
        </div>
        {provider.license_number && (
          <div>
            <span className="font-medium">License:</span> {provider.license_number}
          </div>
        )}
      </div>
    </div>
  );
}

interface ProviderListProps {
  providers: Provider[];
  className?: string;
}

export function ProviderList({ providers, className }: ProviderListProps) {
  if (providers.length === 0) return null;

  return (
    <div className={cn('space-y-3', className)}>
      {providers.map((provider) => (
        <ProviderCard key={provider.id} provider={provider} />
      ))}
    </div>
  );
}

