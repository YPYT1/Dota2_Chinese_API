import { getLuaClasses } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold tracking-tight">{cls.name}</h1>
          {cls.client && <Badge variant="secondary">Client</Badge>}
          {cls.server && <Badge variant="secondary">Server</Badge>}
        </div>
        <p className="text-xl text-muted-foreground">{cls.name_cn}</p>
        <p className="text-base leading-7">{cls.description_cn || cls.description}</p>
      </div>

      {cls.extends && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Extends:</span>
          <Badge variant="outline" className="font-mono">{cls.extends}</Badge>
        </div>
      )}

      {cls.methods && cls.methods.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold tracking-tight px-1">Methods</h2>
          <div className="grid gap-1">
            {cls.methods.map((method) => (
              <div 
                key={method.name} 
                id={method.name} 
                className="group relative flex flex-col gap-2 rounded-lg border border-transparent bg-card p-4 transition-all hover:border-border/50 hover:shadow-sm scroll-mt-32"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                        <circle cx="12" cy="12" r="9" />
                        <path d="M9 12l2 2 4-4" />
                      </svg>
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-primary truncate">
                          {method.name}
                        </span>
                        {method.server && (
                          <span className="inline-flex items-center rounded-md bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-medium text-blue-600 ring-1 ring-inset ring-blue-500/20 dark:text-blue-400">
                            Server
                          </span>
                        )}
                        {method.client && (
                          <span className="inline-flex items-center rounded-md bg-green-500/10 px-1.5 py-0.5 text-[10px] font-medium text-green-600 ring-1 ring-inset ring-green-500/20 dark:text-green-400">
                            Client
                          </span>
                        )}
                      </div>
                      <div className="mt-0.5 text-xs text-muted-foreground font-mono truncate max-w-[600px]">
                        {method.signature}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pl-11">
                  <div className="text-sm text-foreground/90">
                    {method.description_cn || method.description}
                  </div>
                  
                  {method.parameters && method.parameters.length > 0 && (
                    <div className="mt-3 grid gap-2 rounded-md bg-muted/50 p-3 text-xs">
                      {method.parameters.map((param) => (
                        <div key={param.name} className="grid grid-cols-[100px_1fr] gap-2">
                          <span className="font-mono text-primary/80">{param.name}</span>
                          <div className="flex flex-col gap-0.5">
                             <span className="font-mono text-muted-foreground">{param.type}</span>
                             <span className="text-muted-foreground">{param.description_cn || param.description}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    <span className="text-muted-foreground">Returns:</span>
                    <code className="rounded bg-muted px-1 py-0.5 font-mono text-foreground">{method.returnType}</code>
                    <span className="text-muted-foreground">{method.returnDescription_cn}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
