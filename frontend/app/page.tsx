import Link from 'next/link';
import { BrandLogo } from '@/components/brand-logo';
import { branding } from '@/lib/branding';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <BrandLogo size="lg" className="justify-center" />
        </div>
        <p className="text-muted-foreground mb-8">
          {branding.tagline}
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
        >
          Loslegen
        </Link>
      </div>
    </main>
  );
}
