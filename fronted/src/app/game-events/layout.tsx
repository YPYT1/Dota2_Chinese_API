import React from 'react';
import { SimpleSidebar } from '@/components/layout/sidebar';
import { getGameEvents } from '@/lib/data';
import { EventIcon } from '@/components/icons';

import { ContentLayout } from '@/components/layout/content-layout';

export default function GameEventsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const events = getGameEvents();

  const sidebarItems = events.map(e => ({
    name: e.name,
    name_cn: e.name_cn,
    href: `/game-events/${e.name}`,
    icon: <EventIcon className="h-4 w-4" />
  })).sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden bg-background">
      <SimpleSidebar 
        items={sidebarItems} 
        title="Game Events"
        className="hidden lg:block w-72 border-r" 
      />
      <div className="flex-1 overflow-hidden">
        <ContentLayout>
          {children}
        </ContentLayout>
      </div>
    </div>
  );
}
