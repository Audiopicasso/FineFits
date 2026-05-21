export const branding = {
  name: process.env.NEXT_PUBLIC_APP_NAME ?? 'FineFits',
  tagline:
    process.env.NEXT_PUBLIC_APP_TAGLINE ?? 'Deine Looks. Perfekt organisiert.',
  description:
    process.env.NEXT_PUBLIC_APP_DESCRIPTION ??
    'KI-gestützte Garderobenverwaltung und Outfit-Empfehlungen',
  logoPath: '/logo.png',
  storagePrefix: 'finefits',
  userAgent: `${process.env.NEXT_PUBLIC_APP_NAME ?? 'FineFits'}/1.0`,
} as const;

export function unitSystemStorageKey(): string {
  return `${branding.storagePrefix}_unit_system`;
}
