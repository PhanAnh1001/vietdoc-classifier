import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero */}
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-24 text-center">
        <span className="mb-4 inline-block rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 ring-1 ring-blue-200">
          Template
        </span>
        <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-6xl">
          {"{Project Name}"}
        </h1>
        <p className="mb-8 max-w-xl text-lg text-muted-foreground">
          {"{Project description — replace this with your product tagline.}"}
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/register">Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">Sign In</Link>
          </Button>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t px-4 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} {"{Project Name}"}
      </footer>
    </div>
  );
}
