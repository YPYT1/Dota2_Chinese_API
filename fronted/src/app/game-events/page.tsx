import { PageHero3D } from '@/components/ui/page-hero-3d';
import { EventIcon } from '@/components/icons';

export default function GameEventsPage() {
  return (
    <div className="flex flex-col min-h-[80vh]">
      <PageHero3D 
        title="Game Events" 
        description="游戏事件系统文档。监听如 dota_player_killed (玩家击杀)、npc_spawned (单位生成) 等核心事件，实现复杂的游戏流程控制。" 
      />
      
      <div className="flex-1 flex items-center justify-center p-8 opacity-50">
        <div className="flex flex-col items-center gap-4">
          <div className="p-6 bg-muted rounded-3xl">
            <EventIcon className="w-12 h-12 text-muted-foreground" />
          </div>
          <span className="text-base font-medium text-muted-foreground">Game Events Library</span>
        </div>
      </div>
    </div>
  );
}