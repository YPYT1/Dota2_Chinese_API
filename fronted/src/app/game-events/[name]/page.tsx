import { getGameEvents } from '@/lib/data';
import { notFound } from 'next/navigation';
import { MethodItem } from '@/components/api/method-item';

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
    <div className="flex flex-col gap-8 pb-10 max-w-[1600px] mx-auto">
       <div className="flex flex-col gap-0 divide-y divide-border/60 border rounded-xl bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
          <MethodItem method={event as any} />
       </div>
    </div>
  );
}