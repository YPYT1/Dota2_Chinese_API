import { getLuaFunctions } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function generateStaticParams() {
  const functions = getLuaFunctions();
  return functions.map((f) => ({
    name: f.name,
  }));
}

export default async function FunctionPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const functions = getLuaFunctions();
  const func = functions.find((f) => f.name === name);

  if (!func) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold tracking-tight">{func.name}</h1>
          {func.client && <Badge variant="secondary">Client</Badge>}
          {func.server && <Badge variant="secondary">Server</Badge>}
        </div>
        <p className="text-xl text-muted-foreground">{func.name_cn}</p>
        <p className="text-base leading-7">{func.description_cn || func.description}</p>
      </div>

      <Card>
        <CardHeader className="pb-2">
           <div className="text-sm text-muted-foreground font-mono bg-muted/50 p-4 rounded overflow-x-auto">
             {func.signature}
           </div>
        </CardHeader>
        <CardContent>
          {func.parameters && func.parameters.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-2">Parameters</h4>
              <div className="space-y-2">
                {func.parameters.map((param) => (
                  <div key={param.name} className="grid grid-cols-[120px_1fr] gap-4 text-sm border-b border-border/50 pb-2 last:border-0">
                    <div className="font-mono text-primary">{param.name}</div>
                    <div>
                      <div className="font-mono text-xs text-muted-foreground">{param.type}</div>
                      <div>{param.description_cn || param.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 flex items-center gap-2 text-sm">
            <span className="font-semibold">Returns:</span>
            <code className="bg-muted px-1 py-0.5 rounded">{func.returnType}</code>
            <span className="text-muted-foreground">{func.returnDescription_cn}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
