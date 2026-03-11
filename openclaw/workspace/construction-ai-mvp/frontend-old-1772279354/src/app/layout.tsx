import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Construction AI - Smart Intelligence Platform',
  description: 'AI-Powered Construction Intelligence Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="th">
      <body className="antialiased bg-gray-50">
        {children}
      </body>
    </html>
  );
}
