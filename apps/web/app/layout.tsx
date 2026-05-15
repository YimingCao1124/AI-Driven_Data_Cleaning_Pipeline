import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "AI Data Extraction Studio",
  description:
    "A schema-driven, AI-powered data cleaning and structured extraction platform.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <Header />
        <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
        <footer className="mx-auto max-w-6xl px-6 pb-10 text-xs text-slate-500">
          <p>
            AI Data Extraction Studio — V1 MVP. MockLLMClient mode. See the
            project&apos;s <code className="rounded bg-slate-100 px-1 py-0.5">README.md</code>{" "}
            for scope and roadmap.
          </p>
        </footer>
      </body>
    </html>
  );
}
