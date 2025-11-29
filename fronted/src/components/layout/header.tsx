'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Moon, Sun, Search, Menu } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import { GlobalSearch } from '@/components/search/global-search';

const navItems = [
  { name: 'Lua API', href: '/lua-api' },
  { name: 'Game Events', href: '/game-events' },
  { name: 'Panorama API', href: '/panorama-api' },
  { name: 'Panorama Events', href: '/panorama-events' },
];

export function Header() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [globalSearchOpen, setGlobalSearchOpen] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Separate keyboard shortcut for global search if needed, or keep only the button
  // Currently local search uses Cmd+K inside ContentLayout. 
  // Let's use Cmd+Shift+K for global search or just click only.
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'k') {
        e.preventDefault();
        setGlobalSearchOpen(true);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-card/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <Link 
            href="/home" 
            className="flex items-center gap-2 font-semibold text-foreground transition-opacity hover:opacity-70"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-sm font-bold">D2</span>
            </div>
            <span className="hidden sm:inline">Dota2 API</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  pathname === item.href || pathname.startsWith(item.href + '/')
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                {item.name}
              </Link>
            ))}
             {/* Global Search Link Item */}
             <button
                onClick={() => setGlobalSearchOpen(true)}
                className={cn(
                  'rounded-lg px-3 py-2 text-sm font-medium transition-colors text-muted-foreground hover:bg-accent hover:text-accent-foreground flex items-center gap-2'
                )}
              >
                <Search className="h-4 w-4" />
                全局搜索
              </button>
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="h-9 w-9"
            >
              {mounted && (
                theme === 'dark' ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )
              )}
              <span className="sr-only">切换主题</span>
            </Button>

            {/* Mobile Menu */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9 md:hidden">
                  <Menu className="h-4 w-4" />
                  <span className="sr-only">打开菜单</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-72">
                <nav className="flex flex-col gap-2 pt-8">
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        'rounded-lg px-4 py-3 text-sm font-medium transition-colors',
                        pathname === item.href || pathname.startsWith(item.href + '/')
                          ? 'bg-accent text-accent-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )}
                    >
                      {item.name}
                    </Link>
                  ))}
                   <button
                      onClick={() => setGlobalSearchOpen(true)}
                      className={cn(
                        'rounded-lg px-4 py-3 text-sm font-medium transition-colors text-left text-muted-foreground hover:bg-accent hover:text-accent-foreground flex items-center gap-2'
                      )}
                    >
                      <Search className="h-4 w-4" />
                      全局搜索
                    </button>
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>

      {/* Global Search Modal (No Scope = Global) */}
      <GlobalSearch open={globalSearchOpen} onOpenChange={setGlobalSearchOpen} />
    </>
  );
}
