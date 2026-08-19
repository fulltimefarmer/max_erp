"use client";

import { BarChart3, LogOut } from "lucide-react";
import { signOut, useSession } from "next-auth/react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo } from "react";

import { buildNav, navIcon } from "@/components/dashboard/nav";
import { Button } from "@/components/ui/button";
import { fetchBackend } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useDashboardStore } from "@/store/dashboard-store";
import type { Permissions, UserInfo } from "@/types/api";

function Icon({ code }: { code: string }) {
  const Component = navIcon(code);
  return <Component className="h-4 w-4" />;
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  const { permissions, me, setPermissions, setMe } = useDashboardStore();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
      return;
    }
    if (status !== "authenticated" || !session?.accessToken) return;

    let active = true;
    Promise.all([
      fetchBackend<Permissions>("/api/v1/permissions/me", session.accessToken),
      fetchBackend<UserInfo>("/api/v1/auth/me", session.accessToken),
    ])
      .then(([perms, user]) => {
        if (!active) return;
        setPermissions(perms);
        setMe(user);
      })
      .catch(() => {
        if (active) setPermissions(null);
      });

    return () => {
      active = false;
    };
  }, [status, session?.accessToken, router, setPermissions, setMe]);

  const nav = useMemo(
    () => (permissions ? buildNav(permissions.menus, permissions.pages) : []),
    [permissions],
  );

  const currentTitle = useMemo(() => {
    if (pathname === "/dashboard") return "Dashboard";
    const page = permissions?.pages.find(
      (p) => p.route !== "/dashboard" && pathname === `/dashboard${p.route}`,
    );
    return page?.name ?? "Dashboard";
  }, [pathname, permissions]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Loading...
      </div>
    );
  }

  if (status === "unauthenticated") {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-muted/30">
      <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col border-r bg-card">
        <div className="flex h-14 items-center gap-2 border-b px-4">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <BarChart3 className="h-5 w-5" />
          </span>
          <span className="font-semibold">Max ERP</span>
        </div>

        <nav className="flex-1 space-y-4 overflow-y-auto px-3 py-4">
          {nav.map((entry) =>
            entry.kind === "group" ? (
              <div key={entry.menu.id} className="space-y-1">
                <div className="flex items-center gap-2 px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <Icon code={entry.menu.code} />
                  {entry.menu.name}
                </div>
                {entry.children.map((child) => (
                  <Link
                    key={child.menu.id}
                    href={child.link}
                    className={cn(
                      "flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                      pathname === child.link
                        ? "bg-primary/10 font-medium text-primary"
                        : "text-muted-foreground",
                    )}
                  >
                    <Icon code={child.menu.code} />
                    {child.menu.name}
                  </Link>
                ))}
              </div>
            ) : (
              <Link
                key={entry.menu.id}
                href={entry.link}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                  pathname === entry.link
                    ? "bg-primary/10 font-medium text-primary"
                    : "text-muted-foreground",
                )}
              >
                <Icon code={entry.menu.code} />
                {entry.menu.name}
              </Link>
            ),
          )}
        </nav>

        <div className="border-t p-3">
          <Button
            variant="outline"
            className="w-full justify-start gap-2"
            onClick={() => signOut({ callbackUrl: "/" })}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-card px-6">
          <div className="text-sm text-muted-foreground">
            Max ERP <span className="mx-1 text-muted-foreground/60">/</span>
            <span className="font-medium text-foreground">{currentTitle}</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium leading-tight">
                {me?.full_name ?? session?.user?.name ?? "User"}
              </p>
              <p className="text-xs text-muted-foreground">
                {me?.roles?.map((role) => role.name).join(", ") ?? ""}
              </p>
            </div>
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
              {(me?.username ?? session?.user?.name ?? "U").slice(0, 1).toUpperCase()}
            </span>
          </div>
        </header>

        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
