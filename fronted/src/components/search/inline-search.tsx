'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Search } from 'lucide-react';
import {
  Command,
  CommandList,
  CommandGroup,
  CommandItem,
} from '@/components/ui/command';
import { cn } from '@/lib/utils';
import { getAllSearchItems, searchItems, type SearchItem } from '@/lib/data';
import { ClassIcon, FunctionIcon, EnumIcon, ConstantIcon, EventIcon } from '@/components/icons';
import { Badge } from '@/components/ui/badge';

const typeIcons: Record<string, React.ReactNode> = {
  class: <ClassIcon className="h-4 w-4" />,
  function: <FunctionIcon className="h-4 w-4" />,
  enum: <EnumIcon className="h-4 w-4" />,
  constant: <ConstantIcon className="h-4 w-4" />,
  event: <EventIcon className="h-4 w-4" />,
  'panorama-enum': <EnumIcon className="h-4 w-4" />,
  'panorama-event': <EventIcon className="h-4 w-4" />,
};

interface InlineSearchProps {
  className?: string;
  scope?: string;
  placeholder?: string;
}

// Helper for highlighting text
const Highlight = ({ text, query }: { text: string, query: string }) => {
  if (!query || !text) return <>{text}</>;
  // Escape regex characters in query
  const safeQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const parts = text.split(new RegExp(`(${safeQuery})`, 'gi'));
  return (
    <>
      {parts.map((part, i) => 
        part.toLowerCase() === query.toLowerCase() ? (
          <span key={i} className="text-primary font-bold bg-primary/10 rounded-[2px] px-0.5 -mx-0.5">{part}</span>
        ) : (
          part
        )
      )}
    </>
  );
};

export function InlineSearch({ className, scope, placeholder }: InlineSearchProps) {
  const router = useRouter();
  const [query, setQuery] = React.useState('');
  const [results, setResults] = React.useState<SearchItem[]>([]);
  const [open, setOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const allItems = React.useMemo(() => getAllSearchItems(), []);

  const handleSearch = React.useCallback((value: string) => {
    setQuery(value);
    if (!value.trim()) {
      setResults([]);
      setOpen(false);
      return;
    }
    const searchResults = searchItems(value, allItems, { limit: 10, scope });
    setResults(searchResults);
    setOpen(true);
  }, [allItems, scope]);

  const handleSelect = (item: SearchItem) => {
    router.push(item.href);
    setOpen(false);
    setQuery(''); 
  };

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className={cn("relative w-full", className)}>
      <div className="relative group">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
          <Search className="h-4 w-4" />
        </div>
        <input
          className="flex h-10 w-full rounded-xl border border-input/60 bg-muted/30 px-9 py-2 text-sm shadow-sm transition-all placeholder:text-muted-foreground focus-visible:bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:border-ring"
          placeholder={placeholder || "快速搜索..."}
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => { if (query.trim()) setOpen(true); }}
        />
      </div>

      {open && results.length > 0 && (
        <div className="absolute top-full mt-2 w-full rounded-xl border border-border/50 bg-popover/95 backdrop-blur-xl shadow-xl animate-in fade-in zoom-in-95 duration-100 z-50 overflow-hidden">
          <Command shouldFilter={false} className="border-0 rounded-none bg-transparent">
            <CommandList className="max-h-[400px] py-1">
              <CommandGroup heading={scope ? "当前模块结果" : "搜索结果"}>
                {results.map((result) => (
                  <CommandItem
                    key={result.href}
                    value={result.name}
                    onSelect={() => handleSelect(result)}
                    className="flex items-center gap-3 py-2.5 px-3 mx-1 rounded-lg cursor-pointer aria-selected:bg-accent/80"
                  >
                    <span className="text-muted-foreground/80 shrink-0">
                      {typeIcons[result.type]}
                    </span>
                    <div className="flex flex-col min-w-0 flex-1">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-medium text-foreground break-all">
                          <Highlight text={result.name} query={query} />
                        </span>
                        {result.name_cn && (
                          <span className="text-xs text-muted-foreground opacity-70">
                            <Highlight text={result.name_cn} query={query} />
                          </span>
                        )}
                      </div>
                      {result.description && (
                        <div className="text-[10px] text-muted-foreground/60 pr-2 mt-0.5 line-clamp-2">
                          <Highlight text={result.description} query={query} />
                        </div>
                      )}
                    </div>
                    <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-normal text-muted-foreground bg-background/50 ml-auto shrink-0 border-border/40">
                       {result.category}
                    </Badge>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </div>
      )}
    </div>
  );
}
