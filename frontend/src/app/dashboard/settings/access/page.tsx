"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useFetch } from "@/hooks/use-fetch";
import type { ModelAccessRecord } from "@/types/api";

function Check({ value }: { value: boolean }) {
  return value ? (
    <span className="text-green-600">✓</span>
  ) : (
    <span className="text-muted-foreground">—</span>
  );
}

export default function AccessRightsPage() {
  const accesses = useFetch<ModelAccessRecord[]>("/api/v1/model-accesses");

  if (accesses.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access denied</CardTitle>
          <CardDescription>{accesses.error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Access Rights</h1>
        <p className="text-sm text-muted-foreground">
          Per-model permissions for each role
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Model access</CardTitle>
          <CardDescription>{accesses.data?.length ?? 0} rule(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {accesses.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Role</th>
                    <th className="py-2 pr-4 font-medium">Model</th>
                    <th className="py-2 pr-4 text-center font-medium">Create</th>
                    <th className="py-2 pr-4 text-center font-medium">Read</th>
                    <th className="py-2 pr-4 text-center font-medium">Write</th>
                    <th className="py-2 text-center font-medium">Unlink</th>
                  </tr>
                </thead>
                <tbody>
                  {accesses.data?.map((a) => (
                    <tr key={a.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">{a.role_name}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{a.model}</td>
                      <td className="py-2 pr-4 text-center">
                        <Check value={a.perm_create} />
                      </td>
                      <td className="py-2 pr-4 text-center">
                        <Check value={a.perm_read} />
                      </td>
                      <td className="py-2 pr-4 text-center">
                        <Check value={a.perm_write} />
                      </td>
                      <td className="py-2 text-center">
                        <Check value={a.perm_unlink} />
                      </td>
                    </tr>
                  ))}
                  {accesses.data?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-4 text-center text-muted-foreground">
                        No access rules yet.
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
