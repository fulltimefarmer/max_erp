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
import type { Department, Employee, JobPosition } from "@/types/api";

export default function EmployeesPage() {
  const { data: session } = useSession();
  const employees = useFetch<Employee[]>("/api/v1/hr/employees");
  const departments = useFetch<Department[]>("/api/v1/hr/departments");
  const jobs = useFetch<JobPosition[]>("/api/v1/hr/jobs");

  const [form, setForm] = useState({
    name: "",
    work_email: "",
    department_id: "",
    job_id: "",
  });
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (employees.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access denied</CardTitle>
          <CardDescription>{employees.error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!session?.accessToken || !form.name) return;
    setSaving(true);
    setActionError(null);
    try {
      await fetchBackend("/api/v1/hr/employees", session.accessToken, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          work_email: form.work_email || null,
          department_id: form.department_id ? Number(form.department_id) : null,
          job_id: form.job_id ? Number(form.job_id) : null,
        }),
      });
      setForm({ name: "", work_email: "", department_id: "", job_id: "" });
      employees.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!session?.accessToken) return;
    setActionError(null);
    try {
      await fetchBackend(`/api/v1/hr/employees/${id}`, session.accessToken, {
        method: "DELETE",
      });
      employees.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Employees</h1>
        <p className="text-sm text-muted-foreground">Manage your team members</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add employee</CardTitle>
          <CardDescription>Create a new employee record</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Jane Doe"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="work_email">Work email</Label>
              <Input
                id="work_email"
                type="email"
                value={form.work_email}
                onChange={(e) => setForm({ ...form, work_email: e.target.value })}
                placeholder="jane@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="department_id">Department</Label>
              <select
                id="department_id"
                value={form.department_id}
                onChange={(e) => setForm({ ...form, department_id: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              >
                <option value="">—</option>
                {departments.data?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="job_id">Job position</Label>
              <select
                id="job_id"
                value={form.job_id}
                onChange={(e) => setForm({ ...form, job_id: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              >
                <option value="">—</option>
                {jobs.data?.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-2 lg:col-span-4">
              {actionError && <p className="mb-2 text-sm text-destructive">{actionError}</p>}
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Add employee"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Employees</CardTitle>
          <CardDescription>{employees.data?.length ?? 0} employee(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {employees.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Name</th>
                    <th className="py-2 pr-4 font-medium">Email</th>
                    <th className="py-2 pr-4 font-medium">Department</th>
                    <th className="py-2 pr-4 font-medium">Job</th>
                    <th className="py-2 font-medium" />
                  </tr>
                </thead>
                <tbody>
                  {employees.data?.map((emp) => (
                    <tr key={emp.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">{emp.name}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{emp.work_email ?? "—"}</td>
                      <td className="py-2 pr-4 text-muted-foreground">
                        {emp.department_name ?? "—"}
                      </td>
                      <td className="py-2 pr-4 text-muted-foreground">{emp.job_name ?? "—"}</td>
                      <td className="py-2 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-destructive hover:text-destructive"
                          onClick={() => handleDelete(emp.id)}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {employees.data?.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-muted-foreground">
                        No employees yet.
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
