import { Button } from '@/components/livekit/button';

function HealthcareIcon() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      <circle cx="40" cy="40" r="38" fill="#0066CC" fillOpacity="0.1" />
      <path
        d="M40 25C39.4477 25 39 25.4477 39 26V38H27C26.4477 38 26 38.4477 26 39V41C26 41.5523 26.4477 42 27 42H39V54C39 54.5523 39.4477 55 40 55H42C42.5523 55 43 54.5523 43 54V42H55C55.5523 42 56 41.5523 56 41V39C56 38.4477 55.5523 38 55 38H43V26C43 25.4477 42.5523 25 42 25H40Z"
        fill="#0066CC"
      />
      <circle cx="40" cy="40" r="35" stroke="#0066CC" strokeWidth="2" strokeOpacity="0.2" fill="none" />
    </svg>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-background border-input/50 rounded-xl border p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="text-primary mb-3 flex justify-center">{icon}</div>
      <h3 className="text-foreground mb-2 text-center text-sm font-semibold">{title}</h3>
      <p className="text-muted-foreground text-center text-xs leading-relaxed">{description}</p>
    </div>
  );
}

function FeatureIcon({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-primary/10 text-primary flex size-12 items-center justify-center rounded-full">
      {children}
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-50 via-white to-white dark:from-blue-950/20 dark:via-background dark:to-background" />
      
      {/* Subtle pattern overlay */}
      <div className="absolute inset-0 opacity-[0.02] dark:opacity-[0.05]">
        <div className="h-full w-full bg-[radial-gradient(circle_at_1px_1px,_#0066CC_1px,_transparent_0)] bg-[length:40px_40px]" />
      </div>

      {/* Main content */}
      <section className="relative z-10 flex w-full max-w-4xl flex-col items-center justify-center px-6 py-12 text-center">
        {/* Healthcare Icon */}
        <div className="mb-8">
          <HealthcareIcon />
        </div>

        {/* Hero Text */}
        <h1 className="text-foreground mb-4 text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
          Your Healthcare Provider Assistant
        </h1>
        
        <p className="text-muted-foreground mb-8 max-w-2xl text-lg leading-relaxed md:text-xl">
          Find the right healthcare provider for you. Ask questions, get answers, and discover providers that match your needs.
        </p>

        {/* CTA Button */}
        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mb-12 h-14 w-full max-w-xs rounded-full text-base font-semibold shadow-lg transition-all hover:scale-105 hover:shadow-xl md:w-80"
        >
          {startButtonText}
        </Button>

        {/* Features Grid */}
        <div className="grid w-full max-w-3xl grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <FeatureCard
            icon={
              <FeatureIcon>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M12 2L2 7L12 12L22 7L12 2Z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M2 17L12 22L22 17"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M2 12L12 17L22 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </FeatureIcon>
            }
            title="Find Providers by Specialty"
            description="Search by medical specialty, location, or specific conditions"
          />
          
          <FeatureCard
            icon={
              <FeatureIcon>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M22 16.92V19.92C22 20.52 21.52 21 20.92 21H3.08C2.48 21 2 20.52 2 19.92V16.92"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M12 11L12 21"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M12 11L16 7L12 3L8 7L12 11Z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </FeatureIcon>
            }
            title="Get Contact Information"
            description="Access phone numbers, emails, and addresses instantly"
          />
          
          <FeatureCard
            icon={
              <FeatureIcon>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="8" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="2" />
                  <path
                    d="M8 8V6C8 4.89543 8.89543 4 10 4H14C15.1046 4 16 4.89543 16 6V8"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <path d="M8 13H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M8 17H12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </FeatureIcon>
            }
            title="Check Insurance Coverage"
            description="See which insurance plans each provider accepts"
          />
          
          <FeatureCard
            icon={
              <FeatureIcon>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <path
                    d="M12 6V12L16 14"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </FeatureIcon>
            }
            title="24/7 Availability"
            description="Get help finding providers anytime, day or night"
          />
        </div>
      </section>
    </div>
  );
};
