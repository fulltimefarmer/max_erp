"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useFetch } from "@/hooks/use-fetch";
import type { JobPosition } from "@/types/api";

export default function JobsPage() {
  const jobs = useFetch<JobPosition[]>("/api/v1/hr/jobs");

  if (jobs.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access denied</CardTitle>
          <CardDescription>{jobs.error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Job Positions</h1>
        <p className="text-sm text-muted-foreground">Available roles in the company</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Job positions</CardTitle>
          <CardDescription>{jobs.data?.length ?? 0} position(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {jobs.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Name</th>
                    <th className="py-2 pr-4 font-medium">Code</th>
                    <th className="py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.data?.map((j) => (
                    <tr key={j.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">{j.name}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{j.code ?? "—"}</td>
                      <td className="py-2 text-muted-foreground">
                        {j.active ? "Active" : "Inactive"}
                      </td>
                    </tr>
                  ))}
                  {jobs.data?.length === 0 && (
                    <tr>
                      <td colSpan={3} className="py-4 text-center text-muted-foreground">
                        No job positions yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
