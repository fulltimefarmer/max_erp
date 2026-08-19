"use client";

import { useParams } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function PlaceholderPage() {
  const params = useParams<{ slug: string[] }>();
  const slug = params.slug ?? [];
  const title = slug.length > 0 ? slug[slug.length - 1] : "Module";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold capitalize">{title.replace(/-/g, " ")}</h1>
        <p className="text-sm text-muted-foreground">Module</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming soon</CardTitle>
          <CardDescription>
            This module is under construction. Check back later.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The {slug.join(" / ")} module has not been implemented yet.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
