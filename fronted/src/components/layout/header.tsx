'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Moon, Sun, Menu } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import { InlineSearch } from '@/components/search/inline-search';

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

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-card/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <Link 
            href="/home" 
            className="flex items-center gap-2 font-semibold text-foreground transition-opacity hover:opacity-70 mr-4"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-sm font-bold">D2</span>
            </div>
            <span className="hidden sm:inline">Dota2 API</span>
          </Link>

          {/* Desktop Navigation & Search */}
          <div className="flex flex-1 items-center gap-4">
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
             </nav>
             
             {/* Global Search Input */}
             <div className="hidden md:block flex-1 max-w-sm ml-auto">
                <InlineSearch 
                   className="w-full shadow-none border-border/60 bg-muted/50" 
                   placeholder="全局搜索..." 
                />
             </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2 ml-4">
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
                   <div className="px-2 pt-2">
                      <InlineSearch className="w-full" placeholder="全局搜索..." />
                   </div>
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>
    </>
  );
}
