'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';
import { Fragment } from 'react';

const routeNameMap: Record<string, string> = {
  'lua-api': 'Lua API',
  'classes': 'Classes',
  'functions': 'Functions',
  'constants': 'Constants',
  'enums': 'Enums',
  'game-events': 'Game Events',
  'panorama-api': 'Panorama API',
  'panorama-events': 'Panorama Events',
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav className="flex items-center text-sm text-muted-foreground mb-4 overflow-x-auto whitespace-nowrap pb-1">
      <Link href="/home" className="flex items-center hover:text-foreground transition-colors">
        <Home className="h-4 w-4" />
      </Link>
      {segments.map((segment, index) => {
        const href = `/${segments.slice(0, index + 1).join('/')}`;
        const isLast = index === segments.length - 1;
        const name = routeNameMap[segment] || segment;

        return (
          <Fragment key={href}>
            <ChevronRight className="h-4 w-4 mx-1 shrink-0 opacity-50" />
            {isLast ? (
              <span className="font-medium text-foreground">{name}</span>
            ) : (
              <Link href={href} className="hover:text-foreground transition-colors">
                {name}
              </Link>
            )}
          </Fragment>
        );
      })}
    </nav>
  );
}
