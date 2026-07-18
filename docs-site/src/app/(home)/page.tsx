import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
      <h1 className="mb-4 text-3xl font-bold sm:text-4xl">The System Design Primer</h1>
      <p className="mb-8 max-w-2xl text-fd-muted-foreground">
        Learn how to design large-scale systems and prepare for the system design
        interview — now split into short, focused pages by topic.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/docs"
          className="rounded-lg bg-fd-primary px-5 py-2.5 font-medium text-fd-primary-foreground"
        >
          Start reading
        </Link>
        <Link
          href="/docs/scalability/start-here"
          className="rounded-lg border px-5 py-2.5 font-medium"
        >
          System design topics
        </Link>
      </div>
    </main>
  );
}
