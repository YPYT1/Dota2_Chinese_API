'use client';

import React from 'react';

interface PageHero3DProps {
  title: string;
  description?: string;
}

export function PageHero3D({ title, description }: PageHero3DProps) {
  return (
    <div className="relative w-full h-[350px] bg-background/50 overflow-hidden flex flex-col items-center justify-center border-b border-border/40">
       {/* Background Decoration */}
       <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background/80 z-0 pointer-events-none" />
       <div className="absolute inset-0 opacity-30 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent z-0" />

       {/* CSS-based "3D" Metal Text */}
       <h1 
         className="relative z-10 text-6xl md:text-8xl font-black tracking-tighter text-center"
         style={{
           background: 'linear-gradient(to bottom, #ffffff 0%, #a0a0a0 50%, #505050 100%)',
           backgroundClip: 'text',
           WebkitBackgroundClip: 'text',
           color: 'transparent',
           filter: 'drop-shadow(0px 4px 6px rgba(0,0,0,0.3))',
           transform: 'perspective(500px) rotateX(10deg)', // Subtle 3D tilt
         }}
       >
         {title}
       </h1>
       
       {/* Description */}
       {description && (
         <div className="relative z-10 mt-8 px-4 text-center max-w-3xl mx-auto">
            <p className="text-base md:text-lg text-muted-foreground font-medium tracking-wide animate-in fade-in slide-in-from-bottom-4 duration-1000 leading-relaxed">
               {description}
            </p>
         </div>
       )}
    </div>
  );
}