'use client';

import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 sm:p-8 relative overflow-hidden">
      {/* Ambient Background Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] animate-pulse" />
        <motion.div 
          className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent"
          animate={{ 
            opacity: [0.3, 0.6, 0.3],
            scaleX: [0.8, 1.2, 0.8]
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div 
          className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent"
          animate={{ 
            opacity: [0.3, 0.6, 0.3],
            scaleX: [0.8, 1.2, 0.8]
          }}
          transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 text-center space-y-8 max-w-4xl">
        <div className="space-y-4">
          <motion.h1 
            className="text-6xl md:text-8xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-foreground via-primary to-foreground bg-[length:200%_auto]"
            initial={{ opacity: 0, y: 40 }}
            animate={{ 
              opacity: 1, 
              y: 0,
              backgroundPosition: ["0% center", "200% center"]
            }}
            transition={{ 
              opacity: { duration: 0.8, delay: 0.2, ease: "easeOut" },
              y: { duration: 0.8, delay: 0.2, ease: "easeOut" },
              backgroundPosition: { duration: 8, repeat: Infinity, ease: "linear" }
            }}
          >
            Dota2 API Docs
          </motion.h1>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
            className="h-1 w-24 mx-auto bg-gradient-to-r from-transparent via-primary to-transparent rounded-full"
          />

          <motion.p 
            className="text-xl md:text-2xl text-muted-foreground font-light tracking-wide max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.6 }}
          >
            构建下一代 Dota2 模组的终极开发指南
          </motion.p>
        </div>
      </div>
    </div>
  );
}
