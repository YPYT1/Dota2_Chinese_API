'use client';

import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { useEffect, useState, useMemo } from 'react';
import { GlobalSearch } from '@/components/search/global-search';
import { usePathname } from 'next/navigation';

interface ContentLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function ContentLayout({ children, className }: ContentLayoutProps) {
  const [mounted, setMounted] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
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

  // Trigger local search (Cmd+K)
  const handleSearchClick = () => {
    setSearchOpen(true);
  };

  // Listen for Cmd+K to open local search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Search Header */}
      <div className="sticky top-0 z-10 flex-none border-b border-border/40 bg-background/80 px-6 py-4 backdrop-blur-xl">
        <div className="relative mx-auto max-w-[1600px]">
          <Button
            variant="outline"
            className="relative h-10 w-full justify-start bg-muted/50 text-sm font-normal text-muted-foreground shadow-none hover:bg-muted hover:text-foreground sm:pr-12 md:w-full lg:w-full"
            onClick={handleSearchClick}
          >
            <Search className="mr-2 h-4 w-4" />
            <span>搜索当前内容...</span>
            <kbd className="pointer-events-none absolute right-1.5 top-1.5 hidden h-6 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100 sm:flex">
              <span className="text-xs">⌘</span>K
            </kbd>
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className={cn("flex-1 overflow-y-auto", className)}>
        <div className="mx-auto max-w-[1600px] px-6 py-8">
          {children}
        </div>
      </div>

      {/* Context-aware Search Modal */}
      <GlobalSearch 
        open={searchOpen} 
        onOpenChange={setSearchOpen} 
        scope={scope}
      />
    </div>
  );
}
