'use client';

import { useCallback, useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Badge } from '@/components/ui/badge';
import { ClassIcon, FunctionIcon, EnumIcon, ConstantIcon, EventIcon } from '@/components/icons';
import { getAllSearchItems, searchItems, type SearchItem } from '@/lib/data';

export interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  scope?: string; // Add scope prop for context-aware search
}


const typeIcons: Record<string, React.ReactNode> = {
  class: <ClassIcon className="h-4 w-4" />,
  function: <FunctionIcon className="h-4 w-4" />,
  enum: <EnumIcon className="h-4 w-4" />,
  constant: <ConstantIcon className="h-4 w-4" />,
  event: <EventIcon className="h-4 w-4" />,
  'panorama-enum': <EnumIcon className="h-4 w-4" />,
  'panorama-event': <EventIcon className="h-4 w-4" />,
};

const typeLabels: Record<string, string> = {
  class: '类',
  function: '函数',
  enum: '枚举',
  constant: '常量',
  event: '事件',
  'panorama-enum': 'Panorama 枚举',
  'panorama-event': 'Panorama 事件',
};

export function GlobalSearch({ open, onOpenChange, scope }: GlobalSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchItem[]>([]);

  // 预加载所有搜索数据
  const allItems = useMemo(() => getAllSearchItems(), []);

  // 搜索逻辑
  const handleSearch = useCallback((searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }
    
    // Pass scope to searchItems
    const searchResults = searchItems(searchQuery, allItems, { limit: 20, scope });
    setResults(searchResults);
  }, [allItems, scope]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(query);
    }, 150);
    return () => clearTimeout(timeoutId);
  }, [query, handleSearch]);

  const handleSelect = useCallback((result: SearchItem) => {
    onOpenChange(false);
    router.push(result.href);
  }, [router, onOpenChange]);

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <Command className="rounded-lg border-0" shouldFilter={false}>
        <CommandInput 
          placeholder={scope ? `搜索当前模块...` : "搜索类、函数、枚举、事件..."}
          value={query}
          onValueChange={setQuery}
        />
        <CommandList>
          {query && results.length === 0 ? (
            <CommandEmpty>未找到结果</CommandEmpty>
          ) : (
            <>
              {results.length > 0 && (
                <CommandGroup heading="搜索结果">
                  {results.map((result) => (
                    <CommandItem
                      key={result.href}
                      value={result.name}
                      onSelect={() => handleSelect(result)}
                      className="flex items-center gap-3 py-3"
                    >
                      <span className="text-muted-foreground">
                        {typeIcons[result.type]}
                      </span>
                      <div className="flex flex-1 flex-col gap-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{result.name}</span>
                          {result.name_cn && (
                            <span className="text-sm text-muted-foreground">
                              {result.name_cn}
                            </span>
                          )}
                        </div>
                        {result.description && (
                          <span className="text-xs text-muted-foreground line-clamp-1">
                            {result.description}
                          </span>
                        )}
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {typeLabels[result.type]}
                      </Badge>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
              
              {!query && (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  输入关键词搜索所有 API...
                </div>
              )}
            </>
          )}
        </CommandList>
      </Command>
    </CommandDialog>
  );
}
