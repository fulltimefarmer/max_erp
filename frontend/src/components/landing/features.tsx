import {
  BarChart3,
  Boxes,
  FileText,
  ShieldCheck,
  ShoppingCart,
  Users,
} from "lucide-react";

const features = [
  {
    icon: Boxes,
    title: "Inventory management",
    description:
      "Track stock levels, warehouses and movements in real time with automated alerts.",
  },
  {
    icon: ShoppingCart,
    title: "Sales & CRM",
    description:
      "Manage quotes, orders and customer relationships from a single pipeline.",
  },
  {
    icon: FileText,
    title: "Accounting & invoicing",
    description:
      "Automate billing, reconciliation and financial reporting without the busywork.",
  },
  {
    icon: Users,
    title: "Role-based access",
    description:
      "Fine-grained permissions so every team member sees exactly what they need.",
  },
  {
    icon: BarChart3,
    title: "AI-powered insights",
    description:
      "Ask questions in plain language and get answers backed by your business data.",
  },
  {
    icon: ShieldCheck,
    title: "Enterprise security",
    description:
      "JWT authentication, encrypted data and full audit trails out of the box.",
  },
];

export function Features() {
  return (
    <section id="features" className="bg-muted/40 py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need to run your company
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            A complete suite of tools designed for growing teams, from operations to finance.
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border bg-background p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
