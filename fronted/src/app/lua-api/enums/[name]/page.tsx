import { getLuaEnums } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function generateStaticParams() {
  const enums = getLuaEnums();
  return enums.map((e) => ({
    name: e.name,
  }));
}

export default async function EnumPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const enums = getLuaEnums();
  const enumItem = enums.find((e) => e.name === name);

  if (!enumItem) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">{enumItem.name}</h1>
        <p className="text-xl text-muted-foreground">{enumItem.name_cn}</p>
        <p className="text-base leading-7">{enumItem.description_cn || enumItem.description}</p>
      </div>

      {enumItem.members && enumItem.members.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {enumItem.members.map((member) => (
                <div key={member.name} id={member.name} className="grid grid-cols-[1fr_auto_1fr] gap-4 text-sm border-b border-border/50 pb-2 last:border-0 scroll-mt-20">
                  <div className="font-mono text-primary">{member.name}</div>
                  <div className="font-mono text-muted-foreground">= {member.value}</div>
                  <div className="text-muted-foreground">{member.description_cn || member.description}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
