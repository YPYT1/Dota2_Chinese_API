'use client';

import { LuaField } from '@/types/api';

interface FieldItemProps {
  field: LuaField;
}

export function FieldItem({ field }: FieldItemProps) {
  return (
    <div 
      id={field.name}
      className="group flex flex-col gap-2 p-4 transition-colors hover:bg-muted/30 scroll-mt-32"
    >
      <div className="flex items-center gap-2">
        <span className="font-mono font-bold text-foreground">{field.name}</span>
        <span className="font-bold text-muted-foreground">:</span>
        {field.typeLink ? (
           <a href={field.typeLink.replace('#!/vscripts/', '/lua-api/classes/')} className="font-mono text-[#116e51] dark:text-[#4ade80] hover:underline">
             {field.type}
           </a>
        ) : (
           <span className="font-mono text-[#116e51] dark:text-[#4ade80]">{field.type}</span>
        )}
      </div>
      {(field.description_cn || field.notes_cn) && (
        <div className="text-sm text-foreground/80 pl-4 border-l-2 border-border/40">
           <p>{field.description_cn}</p>
           {field.notes_cn && <p className="text-xs text-muted-foreground mt-1">Note: {field.notes_cn}</p>}
        </div>
      )}
    </div>
  );
}
