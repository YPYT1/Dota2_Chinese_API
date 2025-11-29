import type {
  LuaClass,
  LuaFunction,
  LuaEnum,
  LuaConstant,
  GameEvent,
  PanoramaEnum,
  PanoramaEvent,
  DataFile,
} from '@/types/api';

// Import JSON data directly (static import for build time)
import classesData from '../../data/luaapi/classes_cn.json';
import functionsData from '../../data/luaapi/functions_cn.json';
import enumsData from '../../data/luaapi/enums_cn.json';
import constantsData from '../../data/luaapi/constants.json';
import gameEventsData from '../../data/gameevents/events_cn.json';
import panoramaEnumsData from '../../data/panoramaapi/enums.json';
import panoramaEventsData from '../../data/panoramaevents/events.json';

// Lua API Data
export function getLuaClasses(): LuaClass[] {
  return (classesData as DataFile<LuaClass>).items;
}

export function getLuaFunctions(): LuaFunction[] {
  return (functionsData as DataFile<LuaFunction>).items;
}

export function getLuaEnums(): LuaEnum[] {
  return (enumsData as DataFile<LuaEnum>).items;
}

export function getLuaConstants(): LuaConstant[] {
  return (constantsData as DataFile<LuaConstant>).items;
}

// Game Events Data
export function getGameEvents(): GameEvent[] {
  return (gameEventsData as DataFile<GameEvent>).items;
}

// Panorama Data
export function getPanoramaEnums(): PanoramaEnum[] {
  return (panoramaEnumsData as DataFile<PanoramaEnum>).items;
}

export function getPanoramaEvents(): PanoramaEvent[] {
  return (panoramaEventsData as DataFile<PanoramaEvent>).items;
}

import Fuse from 'fuse.js';

// ... (imports remain the same)

// Search types
export interface SearchItem {
  name: string;
  name_cn?: string;
  type: 'class' | 'function' | 'enum' | 'constant' | 'event' | 'panorama-enum' | 'panorama-event';
  category: string;
  scope: 'lua-api' | 'game-events' | 'panorama-api' | 'panorama-events';
  href: string;
  description?: string;
  keywords?: string; // For better fuzzy matching (e.g. member values, params)
}

// Get all searchable items
export function getAllSearchItems(): SearchItem[] {
  const items: SearchItem[] = [];

  // Lua Classes
  getLuaClasses().forEach((cls) => {
    items.push({
      name: cls.name,
      name_cn: cls.name_cn,
      type: 'class',
      category: 'Classes',
      scope: 'lua-api',
      href: `/lua-api/classes/${cls.name}`,
      description: cls.description_cn,
      keywords: cls.methods?.map(m => m.name).join(' '),
    });
    
    // Add methods as searchable items
    cls.methods?.forEach((method) => {
      items.push({
        name: `${cls.name}.${method.name}`,
        name_cn: method.name_cn,
        type: 'function',
        category: 'Methods',
        scope: 'lua-api',
        href: `/lua-api/classes/${cls.name}#${method.name}`,
        description: method.description_cn,
        keywords: method.parameters?.map(p => p.name).join(' '),
      });
    });
  });

  // Lua Functions
  getLuaFunctions().forEach((func) => {
    items.push({
      name: func.name,
      name_cn: func.name_cn,
      type: 'function',
      category: 'Functions',
      scope: 'lua-api',
      href: `/lua-api/functions/${func.name}`,
      description: func.description_cn,
      keywords: func.parameters?.map(p => p.name).join(' '),
    });
  });

  // Lua Enums
  getLuaEnums().forEach((enumItem) => {
    items.push({
      name: enumItem.name,
      name_cn: enumItem.name_cn,
      type: 'enum',
      category: 'Enums',
      scope: 'lua-api',
      href: `/lua-api/enums/${enumItem.name}`,
      description: enumItem.description_cn,
      keywords: enumItem.members?.map(m => `${m.name} ${m.value}`).join(' '),
    });
    
    // Add enum members as searchable
    enumItem.members?.forEach((member) => {
      items.push({
        name: member.name,
        name_cn: member.description_cn,
        type: 'enum',
        category: 'Enum Members',
        scope: 'lua-api',
        href: `/lua-api/enums/${enumItem.name}#${member.name}`,
        description: `${enumItem.name_cn} - 值: ${member.value}`,
      });
    });
  });

  // Lua Constants
  getLuaConstants().forEach((constant) => {
    items.push({
      name: constant.name,
      name_cn: constant.name_cn,
      type: 'constant',
      category: 'Constants',
      scope: 'lua-api',
      href: `/lua-api/constants/${constant.name}`,
      description: constant.description_cn,
      keywords: String(constant.value),
    });
  });

  // Game Events
  getGameEvents().forEach((event) => {
    items.push({
      name: event.name,
      name_cn: event.name_cn,
      type: 'event',
      category: 'Game Events',
      scope: 'game-events',
      href: `/game-events/${event.name}`,
      description: event.description_cn,
      keywords: event.fields?.map(f => f.name).join(' '),
    });
  });

  // Panorama Enums
  getPanoramaEnums().forEach((enumItem) => {
    items.push({
      name: enumItem.name,
      name_cn: enumItem.name_cn,
      type: 'panorama-enum',
      category: 'Panorama Enums',
      scope: 'panorama-api',
      href: `/panorama-api/${enumItem.name}`,
      description: enumItem.description_cn,
      keywords: enumItem.members?.map(m => `${m.name} ${m.value}`).join(' '),
    });
    
    // Add panorama enum members
    enumItem.members?.forEach((member) => {
       items.push({
        name: member.name,
        name_cn: member.description_cn,
        type: 'panorama-enum',
        category: 'Panorama Enum Members',
        scope: 'panorama-api',
        href: `/panorama-api/${enumItem.name}#${member.name}`,
        description: `${enumItem.name_cn} - 值: ${member.value}`,
      });
    });
  });

  // Panorama Events
  getPanoramaEvents().forEach((event) => {
    items.push({
      name: event.name,
      name_cn: event.name_cn,
      type: 'panorama-event',
      category: 'Panorama Events',
      scope: 'panorama-events',
      href: `/panorama-events/${event.name}`,
      description: event.description_cn,
      keywords: event.fields?.map(f => f.name).join(' '),
    });
  });

  return items;
}

// Fuse instance cache
let fuseInstance: Fuse<SearchItem> | null = null;

// Search function using Fuse.js
export function searchItems(query: string, items: SearchItem[], options?: { limit?: number, scope?: string }): SearchItem[] {
  if (!query.trim()) return [];
  
  const { limit = 50, scope } = options || {};

  if (!fuseInstance) {
    fuseInstance = new Fuse(items, {
      keys: [
        { name: 'name', weight: 0.4 },
        { name: 'name_cn', weight: 0.3 },
        { name: 'description', weight: 0.2 },
        { name: 'keywords', weight: 0.1 },
      ],
      threshold: 0.3, // Fuzzy matching threshold (0.0 = perfect match, 1.0 = match anything)
      includeScore: true,
      shouldSort: true,
    });
  }

  let results = fuseInstance.search(query);

  // Filter by scope if provided
  if (scope) {
    results = results.filter(result => result.item.scope === scope);
  }

  return results.slice(0, limit).map(result => result.item);
}
