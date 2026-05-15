import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2 text-lg font-bold text-slate-800">
          <Sparkles className="h-5 w-5 text-brand-600" />
          AI Data Extraction Studio
          <span className="ml-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700">
            V1 MVP
          </span>
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          <Link href="/upload" className="text-slate-600 hover:text-slate-900">
            Upload
          </Link>
          <Link href="/run" className="text-slate-600 hover:text-slate-900">
            Run
          </Link>
          <a
            className="text-slate-600 hover:text-slate-900"
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
          >
            API
          </a>
        </nav>
      </div>
    </header>
  );
}
