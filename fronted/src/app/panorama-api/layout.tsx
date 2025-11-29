import React from 'react';
import { SimpleSidebar } from '@/components/layout/sidebar';
import { getPanoramaEnums } from '@/lib/data';
import { EnumIcon } from '@/components/icons';

import { ContentLayout } from '@/components/layout/content-layout';

export default function PanoramaApiLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const enums = getPanoramaEnums();

  const sidebarItems = enums.map(e => ({
    name: e.name,
    name_cn: e.name_cn,
    href: `/panorama-api/${e.name}`,
    icon: <EnumIcon className="h-4 w-4" />
  })).sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden bg-background">
      <SimpleSidebar 
        items={sidebarItems} 
        title="Panorama Enums"
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
