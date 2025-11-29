import { PageHero3D } from '@/components/ui/page-hero-3d';
import { EnumIcon } from '@/components/icons';

export default function PanoramaApiPage() {
  return (
    <div className="flex flex-col min-h-[80vh]">
      <PageHero3D 
        title="Panorama API" 
        description="Panorama UI 框架的 JavaScript API。控制面板样式、处理用户输入、与游戏逻辑交互，打造现代化的游戏界面。" 
      />
      
      <div className="flex-1 flex items-center justify-center p-8 opacity-50">
        <div className="flex flex-col items-center gap-4">
          <div className="p-6 bg-muted rounded-3xl">
            <EnumIcon className="w-12 h-12 text-muted-foreground" />
          </div>
          <span className="text-base font-medium text-muted-foreground">Panorama JS API</span>
        </div>
      </div>
    </div>
  );
}