import { Public_Sans } from 'next/font/google';
import localFont from 'next/font/local';
import { headers } from 'next/headers';
import type { Metadata } from 'next';
import Script from 'next/script';
import { ThemeToggle } from '@/components/app/theme-toggle';
import { DynamicStyles } from '@/components/app/dynamic-styles';
import { cn, getAppConfig, getStyles, THEME_MEDIA_QUERY, THEME_STORAGE_KEY } from '@/lib/utils';
import '@/styles/globals.css';

const publicSans = Public_Sans({
  variable: '--font-public-sans',
  subsets: ['latin'],
});

const commitMono = localFont({
  display: 'swap',
  variable: '--font-commit-mono',
  src: [
    {
      path: '../fonts/CommitMono-400-Regular.otf',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../fonts/CommitMono-700-Regular.otf',
      weight: '700',
      style: 'normal',
    },
    {
      path: '../fonts/CommitMono-400-Italic.otf',
      weight: '400',
      style: 'italic',
    },
    {
      path: '../fonts/CommitMono-700-Italic.otf',
      weight: '700',
      style: 'italic',
    },
  ],
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export async function generateMetadata(): Promise<Metadata> {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);
  return {
    title: appConfig.pageTitle,
    description: appConfig.pageDescription,
  };
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);
  const styles = getStyles(appConfig);

  const themeScript = `
    (function() {
      const doc = document.documentElement;
      const theme = localStorage.getItem("${THEME_STORAGE_KEY}") ?? "system";

      if (theme === "system") {
        if (window.matchMedia("${THEME_MEDIA_QUERY}").matches) {
          doc.classList.add("dark");
        } else {
          doc.classList.add("light");
        }
      } else {
        doc.classList.add(theme);
      }
    })();
  `.trim().replace(/\n/g, ' ').replace(/\s+/g, ' ');

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        publicSans.variable,
        commitMono.variable,
        'scroll-smooth font-sans antialiased'
      )}
    >
      <body className="overflow-x-hidden">
        <Script
          id="theme-script"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: themeScript,
          }}
        />
        {styles && <DynamicStyles styles={styles} />}
        {children}
        <div className="group fixed bottom-0 left-1/2 z-50 mb-2 -translate-x-1/2">
          <ThemeToggle className="translate-y-20 transition-transform delay-150 duration-300 group-hover:translate-y-0" />
        </div>
      </body>
    </html>
  );
}
