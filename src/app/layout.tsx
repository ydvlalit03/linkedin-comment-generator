import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LinkedIn Comment Generator",
  description:
    "AI-powered tool to generate human-like LinkedIn comments with context-aware analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-gray-50 text-gray-900">
        <Header />
        <main className="flex-1">{children}</main>
        <Toaster position="bottom-right" richColors />
      </body>
    </html>
  );
}

function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <a href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">LC</span>
            </div>
            <span className="font-semibold text-gray-900">
              Comment Generator
            </span>
          </a>
          <nav className="flex items-center gap-6 text-sm">
            <a
              href="/"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Upload
            </a>
            <a
              href="/dashboard"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Dashboard
            </a>
            <a
              href="/analytics"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Analytics
            </a>
            <a
              href="/settings"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Settings
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}
