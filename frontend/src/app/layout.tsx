import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Providers } from "@/providers";

import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Max ERP - The Modern Business Operating System",
  description:
    "Max ERP unifies accounting, inventory, sales and AI-powered insights in one platform.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
