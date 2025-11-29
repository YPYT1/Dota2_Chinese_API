import { getLuaConstants } from '@/lib/data';
import { notFound } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';

export function generateStaticParams() {
  const constants = getLuaConstants();
  return constants.map((c) => ({
    name: c.name,
  }));
}

export default async function ConstantPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const constants = getLuaConstants();
  const constant = constants.find((c) => c.name === name);

  if (!constant) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">{constant.name}</h1>
        <p className="text-xl text-muted-foreground">{constant.name_cn}</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4">
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground">Value</h3>
              <code className="text-lg font-mono bg-muted px-2 py-1 rounded mt-1 block w-fit">
                {constant.value}
              </code>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground">Description</h3>
              <p className="mt-1 text-base">{constant.description_cn || constant.description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
