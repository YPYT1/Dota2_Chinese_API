import { getGameEvents } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function generateStaticParams() {
  const events = getGameEvents();
  return events.map((e) => ({
    name: e.name,
  }));
}

export default async function GameEventPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const events = getGameEvents();
  const event = events.find((e) => e.name === name);

  if (!event) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold tracking-tight">{event.name}</h1>
          <Badge variant="outline">Event</Badge>
        </div>
        <p className="text-xl text-muted-foreground">{event.name_cn}</p>
        <p className="text-base leading-7">{event.description_cn || event.description}</p>
      </div>

      {event.fields && event.fields.length > 0 && (
        <div className="rounded-xl border bg-card">
          <div className="border-b px-4 py-3 text-sm font-semibold text-foreground/80">Parameters</div>
          <div className="divide-y">
            {event.fields.map((field) => (
              <div key={field.name} className="grid grid-cols-[1fr_2fr] gap-4 p-4 text-sm hover:bg-muted/30 sm:grid-cols-[200px_1fr]">
                <div className="flex flex-col gap-1">
                  <span className="font-mono font-medium text-primary">{field.name}</span>
                  <span className="font-mono text-xs text-muted-foreground">{field.type}</span>
                </div>
                <div className="text-muted-foreground">{field.description_cn || field.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
