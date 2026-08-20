import {
  Boxes,
  Briefcase,
  Building2,
  CalendarDays,
  ClipboardCheck,
  LayoutDashboard,
  Receipt,
  Settings,
  ShieldCheck,
  TrendingUp,
  User,
  UserCog,
  Users,
  Wallet,
  type LucideIcon,
} from "lucide-react";

import type { MenuItem, PageItem } from "@/types/api";

export const NAV_ICONS: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  profile: User,
  sales: TrendingUp,
  "sales.orders": Receipt,
  inventory: Boxes,
  "inventory.products": Boxes,
  accounting: Wallet,
  settings: Settings,
  "settings.users": UserCog,
  "settings.access": ShieldCheck,
  hr: Users,
  "hr.employees": Users,
  "hr.departments": Building2,
  "hr.jobs": Briefcase,
  "hr.leaves": CalendarDays,
  "hr.appraisals": ClipboardCheck,
};

export function navIcon(code: string): LucideIcon {
  return NAV_ICONS[code] ?? LayoutDashboard;
}

export function pageLink(menu: MenuItem, pages: PageItem[]): string | null {
  const page = pages.find((p) => p.code === menu.code);
  if (!page) return null;
  return page.code === "dashboard" ? "/dashboard" : `/dashboard${page.route}`;
}

function bySequence(a: MenuItem, b: MenuItem): number {
  return a.sequence - b.sequence;
}

export interface NavLink {
  kind: "link";
  menu: MenuItem;
  link: string;
}

export interface NavGroup {
  kind: "group";
  menu: MenuItem;
  children: NavLink[];
}

export type NavEntry = NavLink | NavGroup;

export function buildNav(menus: MenuItem[], pages: PageItem[]): NavEntry[] {
  const childrenOf = (id: number) =>
    menus.filter((m) => m.parent_id === id).sort(bySequence);

  return menus
    .filter((m) => m.parent_id === null)
    .sort(bySequence)
    .map((menu) => {
      const children = childrenOf(menu.id);
      if (children.length > 0) {
        return {
          kind: "group",
          menu,
          children: children
            .map((child) => ({ kind: "link" as const, menu: child, link: pageLink(child, pages) }))
            .filter((c): c is NavLink => c.link !== null),
        };
      }
      return { kind: "link" as const, menu, link: pageLink(menu, pages) ?? "/dashboard" };
    });
}
