"use client";

import Link from "next/link";
import { useMemo } from "react";

import { navIcon } from "@/components/dashboard/nav";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useDashboardStore } from "@/store/dashboard-store";

export default function DashboardHome() {
  const { me, permissions } = useDashboardStore();

  const modules = useMemo(() => {
    if (!permissions) return [];
    const pageByCode = new Map(permissions.pages.map((p) => [p.code, p]));

    return permissions.menus
      .filter((m) => m.parent_id === null)
      .sort((a, b) => a.sequence - b.sequence)
      .map((menu) => {
        const page = pageByCode.get(menu.code);
        if (page && page.code !== "dashboard") {
          return { menu, link: `/dashboard${page.route}` };
        }
        const child = permissions.menus.find((m) => m.parent_id === menu.id);
        const childPage = child ? pageByCode.get(child.code) : undefined;
        return childPage
          ? { menu, link: `/dashboard${childPage.route}` }
          : null;
      })
      .filter((x): x is { menu: NonNullable<typeof x>["menu"]; link: string } => x !== null);
  }, [permissions]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          Welcome{me?.full_name ? `, ${me.full_name}` : ""}
        </h1>
        <p className="text-sm text-muted-foreground">
          {me?.roles?.length
            ? `Signed in as ${me.username} (${me.roles.map((r) => r.name).join(", ")})`
            : "Signed in"}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {modules.map(({ menu, link }) => {
          const Icon = navIcon(menu.code);
          return (
            <Link key={menu.id} href={link}>
              <Card className="h-full transition-colors hover:border-primary/50 hover:bg-accent/40">
                <CardHeader>
                  <span className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </span>
                  <CardTitle className="text-base">{menu.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>Open {menu.name.toLowerCase()}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      {modules.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>No modules available</CardTitle>
            <CardDescription>
              Your account has no accessible modules. Contact an administrator.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}
