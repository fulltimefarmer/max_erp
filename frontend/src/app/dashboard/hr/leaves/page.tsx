"use client";

import { useSession } from "next-auth/react";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useFetch } from "@/hooks/use-fetch";
import { ApiError, fetchBackend } from "@/lib/api";
import type { Employee, LeaveRequest, LeaveType } from "@/types/api";

function StateBadge({ state }: { state: string }) {
  const styles: Record<string, string> = {
    draft: "bg-secondary text-secondary-foreground",
    approved: "bg-green-100 text-green-700",
    refused: "bg-red-100 text-red-700",
  };
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
        styles[state] ?? "bg-secondary text-secondary-foreground"
      }`}
    >
      {state}
    </span>
  );
}

export default function LeavesPage() {
  const { data: session } = useSession();
  const leaves = useFetch<LeaveRequest[]>("/api/v1/hr/leaves");
  const employees = useFetch<Employee[]>("/api/v1/hr/employees");
  const leaveTypes = useFetch<LeaveType[]>("/api/v1/hr/leave-types");

  const [form, setForm] = useState({
    employee_id: "",
    leave_type_id: "",
    date_from: "",
    date_to: "",
    description: "",
  });
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (leaves.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access denied</CardTitle>
          <CardDescription>{leaves.error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!session?.accessToken || !form.employee_id || !form.leave_type_id || !form.date_from || !form.date_to) {
      return;
    }
    setSaving(true);
    setActionError(null);
    try {
      await fetchBackend("/api/v1/hr/leaves", session.accessToken, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employee_id: Number(form.employee_id),
          leave_type_id: Number(form.leave_type_id),
          date_from: form.date_from,
          date_to: form.date_to,
          description: form.description || null,
        }),
      });
      setForm({ employee_id: "", leave_type_id: "", date_from: "", date_to: "", description: "" });
      leaves.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleAction(id: number, action: "approve" | "refuse" | "delete") {
    if (!session?.accessToken) return;
    setActionError(null);
    try {
      await fetchBackend(`/api/v1/hr/leaves/${id}${action === "delete" ? "" : `/${action}`}`, session.accessToken, {
        method: action === "delete" ? "DELETE" : "POST",
      });
      leaves.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Leaves</h1>
        <p className="text-sm text-muted-foreground">Track and approve time off</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Request leave</CardTitle>
          <CardDescription>Create a new leave request on behalf of an employee</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="employee">Employee</Label>
              <select
                id="employee"
                value={form.employee_id}
                onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                required
              >
                <option value="">—</option>
                {employees.data?.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="leave_type">Leave type</Label>
              <select
                id="leave_type"
                value={form.leave_type_id}
                onChange={(e) => setForm({ ...form, leave_type_id: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                required
              >
                <option value="">—</option>
                {leaveTypes.data?.map((lt) => (
                  <option key={lt.id} value={lt.id}>
                    {lt.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="date_from">From</Label>
              <Input
                id="date_from"
                type="date"
                value={form.date_from}
                onChange={(e) => setForm({ ...form, date_from: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date_to">To</Label>
              <Input
                id="date_to"
                type="date"
                value={form.date_to}
                onChange={(e) => setForm({ ...form, date_to: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2 sm:col-span-2 lg:col-span-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Reason for leave"
              />
            </div>
            <div className="flex items-end sm:col-span-2 lg:col-span-3">
              {actionError && <p className="mb-2 text-sm text-destructive">{actionError}</p>}
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Request leave"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Leave requests</CardTitle>
          <CardDescription>{leaves.data?.length ?? 0} request(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {leaves.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Employee</th>
                    <th className="py-2 pr-4 font-medium">Type</th>
                    <th className="py-2 pr-4 font-medium">From</th>
                    <th className="py-2 pr-4 font-medium">To</th>
                    <th className="py-2 pr-4 font-medium">Days</th>
                    <th className="py-2 pr-4 font-medium">State</th>
                    <th className="py-2 font-medium" />
                  </tr>
                </thead>
                <tbody>
                  {leaves.data?.map((leave) => (
                    <tr key={leave.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">{leave.employee_name}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{leave.leave_type_name}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{leave.date_from}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{leave.date_to}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{leave.number_of_days}</td>
                      <td className="py-2 pr-4">
                        <StateBadge state={leave.state} />
                      </td>
                      <td className="py-2 text-right">
                        {leave.state === "draft" && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-green-600 hover:text-green-700"
                              onClick={() => handleAction(leave.id, "approve")}
                            >
                              Approve
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() => handleAction(leave.id, "refuse")}
                            >
                              Refuse
                            </Button>
                          </>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-muted-foreground hover:text-destructive"
                          onClick={() => handleAction(leave.id, "delete")}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {leaves.data?.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-4 text-center text-muted-foreground">
                        No leave requests yet.
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
