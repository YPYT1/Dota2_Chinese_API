import React from 'react';
import { Sidebar, SidebarGroup, SidebarItem } from '@/components/layout/sidebar';
import { getLuaClasses, getLuaFunctions, getLuaConstants, getLuaEnums } from '@/lib/data';
import { ClassIcon, FunctionIcon, ConstantIcon, EnumIcon } from '@/components/icons';

import { ContentLayout } from '@/components/layout/content-layout';

export default function LuaApiLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const classes = getLuaClasses();
  const functions = getLuaFunctions();
  const constants = getLuaConstants();
  const enums = getLuaEnums();

  const sidebarGroups: SidebarGroup[] = [
    {
      title: 'Classes',
      items: classes.map(c => ({
        name: c.name,
        name_cn: c.name_cn,
        href: `/lua-api/classes/${c.name}`,
        icon: <ClassIcon className="h-4 w-4" />
      })).sort((a, b) => a.name.localeCompare(b.name))
    },
    {
      title: 'Functions',
      items: functions.map(f => ({
        name: f.name,
        name_cn: f.name_cn,
        href: `/lua-api/functions/${f.name}`,
        icon: <FunctionIcon className="h-4 w-4" />
      })).sort((a, b) => a.name.localeCompare(b.name))
    },
    {
      title: 'Constants',
      items: constants.map(c => ({
        name: c.name,
        name_cn: c.name_cn,
        href: `/lua-api/constants/${c.name}`,
        icon: <ConstantIcon className="h-4 w-4" />
      })).sort((a, b) => a.name.localeCompare(b.name))
    },
    {
      title: 'Enums',
      items: enums.map(e => ({
        name: e.name,
        name_cn: e.name_cn,
        href: `/lua-api/enums/${e.name}`,
        icon: <EnumIcon className="h-4 w-4" />
      })).sort((a, b) => a.name.localeCompare(b.name))
    }
  ];

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden bg-background">
      <Sidebar groups={sidebarGroups} className="hidden lg:block w-72 border-r" />
      <div className="flex-1 overflow-hidden">
        <ContentLayout>
          {children}
        </ContentLayout>
      </div>
    </div>
  );
}
