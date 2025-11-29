'use client';

import { FunctionIcon } from '@/components/icons';
import { LuaMethod, LuaFunction, GameEvent, PanoramaEvent } from '@/types/api';

type MethodLike = LuaMethod | LuaFunction | GameEvent | PanoramaEvent;

interface MethodItemProps {
  method: MethodLike;
}

export function MethodItem({ method }: MethodItemProps) {
  // Helper to check if property exists
  const hasServer = 'server' in method;
  const hasClient = 'client' in method;
  const hasOptions = 'options' in method;
  const hasReturnTypeLink = 'returnTypeLink' in method;

  return (
    <div 
      id={method.name}
      className="group flex flex-col gap-3 p-6 transition-colors hover:bg-muted/30 scroll-mt-32"
    >
      {/* Header Row: Signature & Actions */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          {/* Icon */}
          <div className="flex-none mt-1">
             <FunctionIcon className="h-6 w-6 text-muted-foreground/50" />
          </div>

          {/* Signature & Name */}
          <div className="flex flex-col min-w-0">
            {method.name_cn && (
              <span className="text-sm font-medium text-muted-foreground mb-0.5">
                {method.name_cn}
              </span>
            )}
            <div className="font-mono text-base leading-7 break-all">
              <span className="font-bold text-foreground">{method.name}</span>
              <span className="font-bold text-foreground">(</span>
              {method.parameters && method.parameters.map((param, index) => (
                <span key={param.name}>
                  <span className="text-blue-600 dark:text-blue-400 font-medium">{param.name}</span>
                  <span className="font-bold text-foreground">: </span>
                  {/* typeLink check */}
                  {'typeLink' in param && param.typeLink ? (
                    <a 
                      href={param.typeLink.replace('#!/vscripts/', '/lua-api/classes/')}
                      className="text-[#116e51] dark:text-[#4ade80] font-medium hover:underline decoration-[#116e51]/50"
                    >
                      {param.type}
                    </a>
                  ) : (
                    <span className="text-[#116e51] dark:text-[#4ade80] font-medium">{param.type}</span>
                  )}
                  {index < method.parameters.length - 1 && <span className="font-bold text-foreground">, </span>}
                </span>
              ))}
              <span className="font-bold text-foreground">): </span>
              {hasReturnTypeLink && method.returnTypeLink ? (
                <a 
                  href={method.returnTypeLink.replace('#!/vscripts/', '/lua-api/classes/')}
                  className="text-purple-600 dark:text-purple-400 font-bold hover:underline decoration-purple-600/50"
                >
                  {method.returnType}
                </a>
              ) : (
                <span className="text-purple-600 dark:text-purple-400 font-bold">
                  {method.returnType}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Actions Area */}
        <div className="flex items-center gap-2 shrink-0">
          {hasServer && method.server && (
            <div className="flex items-center justify-center h-5 w-5 rounded bg-[#5b82ee] text-white text-[10px] font-bold uppercase" title="Available on server-side Lua">
              S
            </div>
          )}
          {hasClient && method.client && (
            <div className="flex items-center justify-center h-5 w-5 rounded bg-[#59df37] text-white text-[10px] font-bold uppercase" title="Available on client-side Lua">
              C
            </div>
          )}
          
          {/* GitHub Link */}
          {method.githubLink && (
            <a 
              href={method.githubLink}
              target="_blank"
              rel="noreferrer noopener"
              className="text-muted-foreground hover:text-foreground transition-colors p-1"
              title="Search on GitHub"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </a>
          )}

          {/* Google Link */}
          {method.googleLink && (
            <a 
              href={method.googleLink}
              target="_blank"
              rel="noreferrer noopener"
              className="text-muted-foreground hover:text-foreground transition-colors p-1"
              title="Search on Google"
            >
               <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
               </svg>
            </a>
          )}
          
          {/* Link Anchor */}
          <a href={`#${method.name}`} className="text-muted-foreground hover:text-primary transition-colors p-1 opacity-0 group-hover:opacity-100">
            <span className="sr-only">Link</span>
            #
          </a>
        </div>
      </div>

      {/* Description */}
      <div className="pl-9">
        <p className="text-base text-foreground/90 leading-relaxed">
          {method.description_cn || method.description}
        </p>

        {/* Options / EntityBounds Structure */}
        {hasOptions && method.options && method.options.some(opt => opt.name && opt.fields && opt.fields.length > 0) && (
           <div className="mt-4 space-y-3">
              {method.options
                .filter(opt => opt.name && opt.fields && opt.fields.length > 0)
                .map((opt, index) => (
                 <div key={`${opt.name}-${index}`} className="bg-muted/40 rounded-lg border border-border/50 overflow-hidden">
                    {/* Option Header */}
                    <div className="flex items-center gap-2 px-3 py-2 bg-muted/60 border-b border-border/50">
                       <svg viewBox="0 0 16 16" className="h-4 w-4 text-muted-foreground opacity-70">
                          <path fill="currentColor" d="M11.5 12c-1.915 0-3.602-1.241-4.228-3h-1.41a3.11 3.11 0 0 1-2.737 1.625C1.402 10.625 0 9.223 0 7.5s1.402-3.125 3.125-3.125c1.165 0 2.201.639 2.737 1.625h1.41c.626-1.759 2.313-3 4.228-3C13.981 3 16 5.019 16 7.5S13.981 12 11.5 12z"/>
                       </svg>
                       <span className="font-mono text-sm font-bold text-[#116e51] dark:text-[#4ade80]">{opt.name}</span>
                    </div>
                    
                    {/* Option Fields */}
                    <div className="divide-y divide-border/40">
                       {opt.fields.map((field) => (
                          <div key={field.name} className="flex items-center gap-2 px-3 py-2 text-sm font-mono hover:bg-muted/50 transition-colors">
                             <svg viewBox="0 0 16 16" className="h-4 w-4 text-muted-foreground/60">
                                <path fill="currentColor" d="M0 10.736V4.5L9 0l7 3.5v6.236l-9 4.5-7-3.5z"/>
                             </svg>
                             <span className="font-medium text-foreground">{field.name}:</span>
                             {field.typeLink ? (
                                <a href={field.typeLink.replace('#!/vscripts/', '/lua-api/classes/')} className="text-[#116e51] dark:text-[#4ade80] hover:underline">
                                   {field.type}
                                </a>
                             ) : (
                                <span className="text-[#116e51] dark:text-[#4ade80]">{field.type}</span>
                             )}
                             {field.description_cn && (
                                <span className="text-muted-foreground ml-2 font-sans">- {field.description_cn}</span>
                             )}
                          </div>
                       ))}
                    </div>
                 </div>
              ))}
           </div>
        )}
      </div>
    </div>
  );
}