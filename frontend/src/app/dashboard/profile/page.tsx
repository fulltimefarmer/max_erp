"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useDashboardStore } from "@/store/dashboard-store";

export default function ProfilePage() {
  const { me } = useDashboardStore();

  if (!me) {
    return <p className="text-muted-foreground">Loading profile...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">My Profile</h1>
        <p className="text-sm text-muted-foreground">Your personal information</p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle>{me.full_name ?? me.username}</CardTitle>
          <CardDescription>@{me.username}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="grid grid-cols-[120px_1fr] gap-2">
            <span className="text-muted-foreground">Email</span>
            <span>{me.email}</span>
          </div>
          <div className="grid grid-cols-[120px_1fr] gap-2">
            <span className="text-muted-foreground">Full name</span>
            <span>{me.full_name ?? "—"}</span>
          </div>
          <div className="grid grid-cols-[120px_1fr] gap-2">
            <span className="text-muted-foreground">Status</span>
            <span>{me.is_active ? "Active" : "Inactive"}</span>
          </div>
          <div className="grid grid-cols-[120px_1fr] gap-2">
            <span className="text-muted-foreground">Roles</span>
            <div className="flex flex-wrap gap-1">
              {me.roles.map((role) => (
                <span
                  key={role.id}
                  className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium"
                >
                  {role.name}
                </span>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
