'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface OnThisPageProps {
  sections: { id: string; label: string }[];
}

export function OnThisPage({ sections }: OnThisPageProps) {
  const [activeId, setActiveId] = useState<string>('');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: '-20% 0% -35% 0%' }
    );

    sections.forEach(({ id }) => {
      const element = document.getElementById(id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [sections]);

  if (sections.length === 0) return null;

  return (
    <div className="hidden xl:block w-48 shrink-0 pl-8 border-l border-border/40">
      <div className="sticky top-6 space-y-3">
        <p className="text-xs font-bold uppercase text-foreground tracking-wider">On This Page</p>
        <div className="flex flex-col space-y-2">
          {sections.map(({ id, label }) => (
            <a
              key={id}
              href={`#${id}`}
              className={cn(
                "text-xs transition-colors block truncate",
                activeId === id ? "text-primary font-bold" : "text-foreground/70 hover:text-foreground font-medium"
              )}
              onClick={(e) => {
                e.preventDefault();
                document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
                setActiveId(id);
              }}
            >
              {label}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
