import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "น้องอุ่นใจ - Ecosystem Dashboard",
  description: "ระบบนิเวศน์น้องอุ่นใจ - Executive Strategic Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" 
          rel="stylesheet" 
        />
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: "'Kanit', sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
