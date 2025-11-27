export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Healthcare Assistant',
  pageTitle: 'Healthcare Provider Assistant - Find Your Perfect Healthcare Provider',
  pageDescription: 'Your friendly voice AI assistant helping you discover and connect with healthcare providers. Find providers by specialty, location, insurance coverage, and more.',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#0066CC',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#0088FF',
  startButtonText: 'Start Conversation',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
