import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-card/50">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-center px-4 sm:px-6 lg:px-8">
        <p className="text-sm text-muted-foreground">
          Design by{' '}
          <Link 
            href="https://github.com/LiamWang" 
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-foreground hover:text-primary transition-colors"
          >
            LiamWang
          </Link>
          {' '}© {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
