'use client';

import { useEffect } from 'react';

interface DynamicStylesProps {
  styles: string;
}

export function DynamicStyles({ styles }: DynamicStylesProps) {
  useEffect(() => {
    if (!styles) return;

    const styleId = 'dynamic-app-styles';
    let styleElement = document.getElementById(styleId) as HTMLStyleElement;

    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      document.head.appendChild(styleElement);
    }

    styleElement.textContent = styles;

    return () => {
      // Cleanup on unmount
      const element = document.getElementById(styleId);
      if (element) {
        element.remove();
      }
    };
  }, [styles]);

  return null;
}

