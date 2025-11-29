import { getLuaClasses } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { MethodItem } from '@/components/api/method-item';
import { FieldItem } from '@/components/api/field-item';
import { OnThisPage } from '@/components/layout/on-this-page';

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

  const sections = [
    ...(cls.fields && cls.fields.length > 0 ? [{ id: 'fields-header', label: 'Fields' }] : []),
    ...(cls.methods && cls.methods.length > 0 ? [{ id: 'methods-header', label: 'Methods' }] : []),
    ...(cls.methods?.map(m => ({ id: m.name, label: m.name })) || [])
  ];

  return (
    <div className="flex gap-12 pb-10 max-w-[1600px] mx-auto">
      <div className="flex-1 flex flex-col gap-8 min-w-0">
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
                    {cls.extendsLink ? (
                      <a 
                        href={cls.extendsLink.replace('#!/vscripts/', '/lua-api/classes/')}
                        className="hover:underline"
                      >
                        <Badge variant="outline" className="font-mono text-xs hover:bg-primary/10 transition-colors">
                          {cls.extends}
                        </Badge>
                      </a>
                    ) : (
                      <Badge variant="outline" className="font-mono text-xs">{cls.extends}</Badge>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
          <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
            {cls.description_cn || cls.description}
          </p>
        </div>

        {/* Fields List Section */}
        {cls.fields && cls.fields.length > 0 && (
          <div className="space-y-6" id="fields-header">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold tracking-tight flex items-center gap-2">
                Fields
                <Badge variant="secondary" className="rounded-full px-2.5">{cls.fields.length}</Badge>
              </h2>
            </div>
            
            <div className="flex flex-col gap-0 divide-y divide-border/60 border rounded-xl bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
              {cls.fields.map((field) => (
                <FieldItem key={field.name} field={field} />
              ))}
            </div>
          </div>
        )}

        {/* Methods List Section */}
        {cls.methods && cls.methods.length > 0 && (
          <div className="space-y-6" id="methods-header">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold tracking-tight flex items-center gap-2">
                Methods
                <Badge variant="secondary" className="rounded-full px-2.5">{cls.methods.length}</Badge>
              </h2>
            </div>
            
            <div className="flex flex-col gap-0 divide-y divide-border/60 border rounded-xl bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
              {cls.methods.map((method) => (
                <MethodItem key={method.name} method={method} />
              ))}
            </div>
          </div>
        )}
      </div>
      
      <OnThisPage sections={sections} />
    </div>
  );
}
