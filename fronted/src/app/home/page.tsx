'use client';

import { cn } from '@/lib/utils';
import Scene3D from './Scene3D';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* 3D Scene Background */}
      <Scene3D />
      
      {/* Ambient Overlay (Optional) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-10 opacity-30">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" />
      </div>
    </div>
  );
}
