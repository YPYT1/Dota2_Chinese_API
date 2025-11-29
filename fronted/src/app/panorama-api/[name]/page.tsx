import { getPanoramaEnums } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function generateStaticParams() {
  const enums = getPanoramaEnums();
  return enums.map((e) => ({
    name: e.name,
  }));
}

export default async function PanoramaEnumPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const enums = getPanoramaEnums();
  const enumItem = enums.find((e) => e.name === name);

  if (!enumItem) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">{enumItem.name}</h1>
        <p className="text-xl text-muted-foreground">{enumItem.name_cn}</p>
        <p className="text-base leading-7">{enumItem.description_cn}</p>
      </div>

      {enumItem.members && enumItem.members.length > 0 && (
        <div className="rounded-xl border bg-card">
          <div className="border-b px-4 py-3 text-sm font-semibold text-foreground/80">Members</div>
          <div className="divide-y">
            {enumItem.members.map((member) => (
              <div key={member.name} className="grid grid-cols-[1fr_auto_2fr] gap-4 p-4 text-sm hover:bg-muted/30">
                <span className="font-mono font-medium text-primary">{member.name}</span>
                <span className="font-mono text-muted-foreground">= {member.value}</span>
                <span className="text-muted-foreground">{member.description_cn}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
