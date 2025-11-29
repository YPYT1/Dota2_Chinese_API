import { PageHero3D } from '@/components/ui/page-hero-3d';
import { EventIcon } from '@/components/icons';

export default function PanoramaEventsPage() {
  return (
    <div className="flex flex-col min-h-[80vh]">
      <PageHero3D 
        title="Panorama Events" 
        description="前端面板事件系统。处理 UI 事件、自定义事件通信，实现 Lua 后端与 Panorama 前端的双向数据流。" 
      />
      
      <div className="flex-1 flex items-center justify-center p-8 opacity-50">
        <div className="flex flex-col items-center gap-4">
          <div className="p-6 bg-muted rounded-3xl">
            <EventIcon className="w-12 h-12 text-muted-foreground" />
          </div>
          <span className="text-base font-medium text-muted-foreground">Panorama Events</span>
        </div>
      </div>
    </div>
  );
}