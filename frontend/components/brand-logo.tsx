import { branding } from '@/lib/branding';
import { cn } from '@/lib/utils';

const sizeStyles = {
  sm: { icon: 'h-8 w-8', text: 'text-xl' },
  sidebar: { icon: 'h-16 w-16', text: 'text-xl' },
  md: { icon: 'h-16 w-16', text: 'text-3xl' },
  lg: { icon: 'h-24 w-24', text: 'text-4xl' },
} as const;

interface BrandLogoProps {
  size?: keyof typeof sizeStyles;
  showName?: boolean;
  className?: string;
  nameClassName?: string;
  iconClassName?: string;
}

export function BrandLogo({
  size = 'sm',
  showName = true,
  className,
  nameClassName,
  iconClassName,
}: BrandLogoProps) {
  const styles = sizeStyles[size];

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <img
        src={branding.logoPath}
        alt={branding.name}
        className={cn(styles.icon, 'shrink-0 object-contain', iconClassName)}
      />
      {showName && (
        <span className={cn('font-bold tracking-tight', styles.text, nameClassName)}>
          {branding.name}
        </span>
      )}
    </div>
  );
}
