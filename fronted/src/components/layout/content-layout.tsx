'use client';

import { useState, useEffect, useMemo } from 'react';
import { InlineSearch } from '@/components/search/inline-search';
import { Breadcrumbs } from '@/components/layout/breadcrumbs';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface ContentLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function ContentLayout({ children, className }: ContentLayoutProps) {
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  
  // Determine scope based on pathname
  const scope = useMemo(() => {
    if (pathname.startsWith('/lua-api')) return 'lua-api';
    if (pathname.startsWith('/game-events')) return 'game-events';
    if (pathname.startsWith('/panorama-api')) return 'panorama-api';
    if (pathname.startsWith('/panorama-events')) return 'panorama-events';
    return undefined;
  }, [pathname]);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Main Content & Search - Scrollable Wrapper */}
      <div className={cn("flex-1 overflow-y-auto", className)}>
        {/* Search Header */}
        <div className="relative z-20 border-b border-border/40 bg-background/80 px-6 py-4 backdrop-blur-xl">
          <div className="relative mx-auto max-w-[1600px]">
            <InlineSearch 
              className="w-full max-w-md shadow-sm" 
              scope={scope} 
              placeholder="搜索当前内容..." 
            />
          </div>
        </div>

        {/* Page Content */}
        <div className="relative z-0 mx-auto max-w-[1600px] px-6 py-8">
          <Breadcrumbs />
          {children}
        </div>
      </div>
    </div>
  );
}
