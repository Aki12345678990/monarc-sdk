import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter, Inter_Tight, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import { MotionRoot } from "@/components/motion/MotionRoot";
import "./globals.css";

const interTight = Inter_Tight({
  variable: "--font-inter-tight",
  weight: ["600", "700"],
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "APK SDK footprint analyser (research prototype)",
  description:
    "Static analysis of an Android APK's third-party SDK footprint and attack-surface facts.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      className={`${interTight.variable} ${inter.variable} ${jetbrains.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <div className="bg-scene" aria-hidden>
          <div className="blob blob-a" />
          <div className="blob blob-b" />
          <div className="blob blob-c" />
          <div className="noise" />
        </div>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "(function(){var r=document.documentElement;function v(){r.classList.toggle('is-paused',document.hidden);}v();document.addEventListener('visibilitychange',v);document.addEventListener('pointermove',function(e){var t=e.target;if(!t||!t.closest)return;var p=t.closest('.panel, .card');if(!p)return;var b=p.getBoundingClientRect();p.style.setProperty('--spot-x',(e.clientX-b.left)+'px');p.style.setProperty('--spot-y',(e.clientY-b.top)+'px');},{passive:true});})();",
          }}
        />
        <div className="site-shell flex min-h-full flex-1 flex-col">
          <header className="sticky top-3 z-20 mx-4">
            <div className="panel site-measure mx-auto flex items-center justify-between !py-3">
              <Link href="/" className="chrome-text font-display text-2xl no-underline">
                Monarc
              </Link>
              <nav className="flex items-center gap-4 text-sm">
                <Link href="/method">Method</Link>
                <span className="text-muted">Research prototype</span>
              </nav>
            </div>
          </header>
          <main className="site-measure mx-auto w-full flex-1 px-4 py-8">
            <MotionRoot>{children}</MotionRoot>
          </main>
          <footer className="mt-4 border-t border-edge-lo">
            <p className="site-measure mx-auto px-4 py-4 text-sm text-muted">
              MSc Cyber Security dissertation prototype. Static analysis only.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}
