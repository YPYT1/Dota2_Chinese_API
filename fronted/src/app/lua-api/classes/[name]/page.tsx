import { getLuaClasses } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { FunctionIcon } from '@/components/icons';

export function generateStaticParams() {
  const classes = getLuaClasses();
  return classes.map((c) => ({
    name: c.name,
  }));
}

export default async function ClassPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const classes = getLuaClasses();
  const cls = classes.find((c) => c.name === name);

  if (!cls) {
    notFound();
  }

  return (
    <div className="flex flex-col gap-8 pb-10 max-w-[1600px] mx-auto">
      {/* Header Section */}
      <div className="flex flex-col gap-4 border-b pb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <line x1="7" y1="8" x2="17" y2="8" />
              <line x1="7" y1="12" x2="14" y2="12" />
              <line x1="7" y1="16" x2="11" y2="16" />
            </svg>
          </div>
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">{cls.name}</h1>
            <div className="flex items-center gap-2">
              {cls.client && <Badge variant="secondary" className="bg-green-500/10 text-green-700 hover:bg-green-500/20 dark:text-green-400">Client</Badge>}
              {cls.server && <Badge variant="secondary" className="bg-blue-500/10 text-blue-700 hover:bg-blue-500/20 dark:text-blue-400">Server</Badge>}
              {cls.extends && (
                <>
                  <Separator orientation="vertical" className="h-4" />
                  <span className="text-sm text-muted-foreground">Extends</span>
                  <Badge variant="outline" className="font-mono text-xs">{cls.extends}</Badge>
                </>
              )}
            </div>
          </div>
        </div>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          {cls.description_cn || cls.description}
        </p>
      </div>

      {/* Methods List Section */}
      {cls.methods && cls.methods.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight flex items-center gap-2">
              Methods
              <Badge variant="secondary" className="rounded-full px-2.5">{cls.methods.length}</Badge>
            </h2>
          </div>
          
          <div className="flex flex-col gap-0 divide-y divide-border/60 border rounded-xl bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
            {cls.methods.map((method) => (
              <div 
                key={method.name} 
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

                    {/* Signature */}
                    <div className="font-mono text-base leading-7 break-all">
                      <span className="font-bold text-foreground">{method.name}</span>
                      <span className="font-bold text-foreground">(</span>
                      {method.parameters && method.parameters.map((param, index) => (
                        <span key={param.name}>
                          <span className="text-blue-600 dark:text-blue-400 font-medium">{param.name}</span>
                          {index < method.parameters.length - 1 && <span className="font-bold text-foreground">, </span>}
                        </span>
                      ))}
                      <span className="font-bold text-foreground">): </span>
                      <span className="text-purple-600 dark:text-purple-400 font-bold">
                        {method.returnType}
                      </span>
                    </div>
                  </div>

                  {/* Actions Area */}
                  <div className="flex items-center gap-2 shrink-0">
                    {method.server && (
                      <div className="flex items-center justify-center h-5 w-5 rounded bg-[#5b82ee] text-white text-[10px] font-bold uppercase" title="Available on server-side Lua">
                        S
                      </div>
                    )}
                    {method.client && (
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
                  {method.options && method.options.length > 0 && (
                     <div className="mt-4 space-y-3">
                        {method.options.map((opt) => (
                           <div key={opt.name} className="bg-muted/40 rounded-lg border border-border/50 overflow-hidden">
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
                                          <a href={field.typeLink} className="text-[#116e51] dark:text-[#4ade80] hover:underline">
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
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
