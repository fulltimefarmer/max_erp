import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section id="product" className="relative overflow-hidden">
      <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6 sm:py-32">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            The modern operating system for your business
          </h1>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Max ERP unifies accounting, inventory, sales and customer data into one
            intelligent platform — with AI-driven insights that help you make better
            decisions, faster.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" asChild>
              <Link href="/login">
                Get started
                <ArrowRight />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="#features">Learn more</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
