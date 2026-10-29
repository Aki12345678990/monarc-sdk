import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Anton, Source_Sans_3 } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const anton = Anton({
  variable: "--font-anton",
  weight: "400",
  subsets: ["latin"],
});

const sourceSans = Source_Sans_3({
  variable: "--font-source-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "APK SDK footprint analyser (research prototype)",
  description:
    "Static analysis of an Android APK's third-party SDK footprint and attack-surface facts.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${anton.variable} ${sourceSans.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <header className="border-b border-charcoal/20">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
            <Link href="/" className="font-display text-2xl text-charcoal no-underline">
              APK SDK footprint analyser
            </Link>
            <span className="text-sm">Research prototype</span>
          </div>
        </header>
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
        <footer className="border-t border-charcoal/20">
          <p className="mx-auto max-w-5xl px-4 py-4 text-sm">
            MSc Cyber Security dissertation prototype. Static analysis only.
          </p>
        </footer>
      </body>
    </html>
  );
}
