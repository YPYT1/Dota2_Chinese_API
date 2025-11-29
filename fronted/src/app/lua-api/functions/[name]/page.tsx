import { getLuaFunctions } from '@/lib/data';
import { notFound } from 'next/navigation';
import { MethodItem } from '@/components/api/method-item';

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
    <div className="flex flex-col gap-8 pb-10 max-w-[1600px] mx-auto">
       <div className="flex flex-col gap-0 divide-y divide-border/60 border rounded-xl bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
          <MethodItem method={func} />
       </div>
    </div>
  );
}