import { ClassIcon, FunctionIcon, ConstantIcon, EnumIcon } from '@/components/icons';

export default function LuaApiPage() {
  return (
    <div className="flex flex-col items-center justify-center h-[50vh] text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Lua API</h1>
      <p className="mt-2 text-muted-foreground max-w-md">
        Select a class, function, constant, or enum from the sidebar to view its documentation.
      </p>
      <div className="mt-8 grid grid-cols-4 gap-4 opacity-50">
        <div className="flex flex-col items-center gap-2">
          <div className="p-3 bg-muted rounded-lg">
            <ClassIcon className="w-6 h-6" />
          </div>
          <span className="text-xs">Classes</span>
        </div>
        <div className="flex flex-col items-center gap-2">
          <div className="p-3 bg-muted rounded-lg">
            <FunctionIcon className="w-6 h-6" />
          </div>
          <span className="text-xs">Functions</span>
        </div>
        <div className="flex flex-col items-center gap-2">
          <div className="p-3 bg-muted rounded-lg">
            <ConstantIcon className="w-6 h-6" />
          </div>
          <span className="text-xs">Constants</span>
        </div>
        <div className="flex flex-col items-center gap-2">
          <div className="p-3 bg-muted rounded-lg">
            <EnumIcon className="w-6 h-6" />
          </div>
          <span className="text-xs">Enums</span>
        </div>
      </div>
    </div>
  );
}
