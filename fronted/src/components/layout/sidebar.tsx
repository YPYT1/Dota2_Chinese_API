'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

export interface SidebarItem {
  name: string;
  name_cn?: string;
  href: string;
  icon?: React.ReactNode;
  items?: SidebarItem[];
}

export interface SidebarGroup {
  title: string;
  items: SidebarItem[];
  defaultOpen?: boolean;
}

interface SidebarProps {
  groups: SidebarGroup[];
  className?: string;
}

function SidebarGroupComponent({ 
  group, 
  pathname 
}: { 
  group: SidebarGroup; 
  pathname: string;
}) {
  const [isOpen, setIsOpen] = useState(group.defaultOpen ?? true);
  const hasActiveItem = group.items.some(item => pathname === item.href);

  return (
    <div className="pb-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="sticky top-0 z-10 bg-sidebar/95 backdrop-blur-sm flex w-full items-center justify-between px-3 py-2 text-xs font-bold uppercase tracking-wider text-foreground hover:bg-muted/50 transition-colors border-b border-border/10"
      >
        {group.title}
        <ChevronDown 
          className={cn(
            "h-3 w-3 transition-transform duration-200 opacity-50",
            isOpen ? "" : "-rotate-90"
          )} 
        />
      </button>
      {isOpen && (
        <div className="mt-0.5 space-y-[1px]">
          {group.items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2 rounded-md px-3 py-1.5 text-[13px] font-medium transition-colors',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              {item.icon}
              <span className="truncate">{item.name}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function Sidebar({ groups, className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className={cn(
      "hidden w-64 shrink-0 border-r border-border/40 bg-sidebar lg:block",
      className
    )}>
      <ScrollArea className="h-[calc(100vh-3.5rem)] py-4 px-2">
        {groups.map((group, index) => (
          <SidebarGroupComponent 
            key={index} 
            group={group} 
            pathname={pathname}
          />
        ))}
      </ScrollArea>
    </aside>
  );
}

// Simple list sidebar for pages like Events
interface SimpleSidebarProps {
  items: SidebarItem[];
  title?: string;
  className?: string;
}

export function SimpleSidebar({ items, title, className }: SimpleSidebarProps) {
  const pathname = usePathname();

  return (
    <aside className={cn(
      "hidden w-64 shrink-0 border-r border-border/40 bg-sidebar lg:block",
      className
    )}>
      <ScrollArea className="h-[calc(100vh-3.5rem)] py-4 px-2">
        {title && (
          <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/80">
            {title}
          </div>
        )}
        <div className="mt-0.5 space-y-[1px]">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2 rounded-md px-3 py-1.5 text-[13px] font-medium transition-colors',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              {item.icon}
              <span className="truncate">{item.name}</span>
            </Link>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
