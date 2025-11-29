import { PageHero3D } from '@/components/ui/page-hero-3d';
import { ClassIcon, FunctionIcon, ConstantIcon, EnumIcon } from '@/components/icons';

export default function LuaApiPage() {
  return (
    <div className="flex flex-col min-h-[80vh]">
      <PageHero3D 
        title="Lua API" 
        description="Dota 2 Lua 脚本开发的核心 API 文档。包含所有服务器端类、全局函数、常量定义及枚举类型，是编写自定义游戏逻辑的基础。" 
      />
      
      <div className="flex-1 flex items-center justify-center p-8 opacity-50 hover:opacity-100 transition-opacity duration-500">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-16 text-center">
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-muted rounded-2xl">
              <ClassIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Classes</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-muted rounded-2xl">
              <FunctionIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Functions</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-muted rounded-2xl">
              <ConstantIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Constants</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-muted rounded-2xl">
              <EnumIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Enums</span>
          </div>
        </div>
      </div>
    </div>
  );
}