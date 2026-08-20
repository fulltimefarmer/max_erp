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
import type { Appraisal, Employee } from "@/types/api";

function StateBadge({ state }: { state: string }) {
  const styles: Record<string, string> = {
    draft: "bg-secondary text-secondary-foreground",
    done: "bg-green-100 text-green-700",
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

export default function AppraisalsPage() {
  const { data: session } = useSession();
  const appraisals = useFetch<Appraisal[]>("/api/v1/hr/appraisals");
  const employees = useFetch<Employee[]>("/api/v1/hr/employees");

  const [form, setForm] = useState({
    employee_id: "",
    appraisal_date: "",
    final_rating: "",
    goals: "",
    feedback: "",
  });
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (appraisals.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Access denied</CardTitle>
          <CardDescription>{appraisals.error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!session?.accessToken || !form.employee_id || !form.appraisal_date) return;
    setSaving(true);
    setActionError(null);
    try {
      await fetchBackend("/api/v1/hr/appraisals", session.accessToken, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employee_id: Number(form.employee_id),
          appraisal_date: form.appraisal_date,
          final_rating: form.final_rating ? Number(form.final_rating) : null,
          goals: form.goals || null,
          feedback: form.feedback || null,
        }),
      });
      setForm({
        employee_id: "",
        appraisal_date: "",
        final_rating: "",
        goals: "",
        feedback: "",
      });
      appraisals.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleComplete(id: number) {
    if (!session?.accessToken) return;
    setActionError(null);
    try {
      await fetchBackend(`/api/v1/hr/appraisals/${id}/complete`, session.accessToken, {
        method: "POST",
      });
      appraisals.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    }
  }

  async function handleDelete(id: number) {
    if (!session?.accessToken) return;
    setActionError(null);
    try {
      await fetchBackend(`/api/v1/hr/appraisals/${id}`, session.accessToken, {
        method: "DELETE",
      });
      appraisals.refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Appraisals</h1>
        <p className="text-sm text-muted-foreground">Employee performance reviews</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New appraisal</CardTitle>
          <CardDescription>Start a performance review for an employee</CardDescription>
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
              <Label htmlFor="appraisal_date">Date</Label>
              <Input
                id="appraisal_date"
                type="date"
                value={form.appraisal_date}
                onChange={(e) => setForm({ ...form, appraisal_date: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="final_rating">Rating (1-5)</Label>
              <select
                id="final_rating"
                value={form.final_rating}
                onChange={(e) => setForm({ ...form, final_rating: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              >
                <option value="">—</option>
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2 sm:col-span-2 lg:col-span-3">
              <Label htmlFor="goals">Goals</Label>
              <Input
                id="goals"
                value={form.goals}
                onChange={(e) => setForm({ ...form, goals: e.target.value })}
                placeholder="Objectives for the review period"
              />
            </div>
            <div className="space-y-2 sm:col-span-2 lg:col-span-3">
              <Label htmlFor="feedback">Feedback</Label>
              <Input
                id="feedback"
                value={form.feedback}
                onChange={(e) => setForm({ ...form, feedback: e.target.value })}
                placeholder="Manager comments"
              />
            </div>
            <div className="sm:col-span-2 lg:col-span-3">
              {actionError && <p className="mb-2 text-sm text-destructive">{actionError}</p>}
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Create appraisal"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appraisals</CardTitle>
          <CardDescription>{appraisals.data?.length ?? 0} review(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {appraisals.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Employee</th>
                    <th className="py-2 pr-4 font-medium">Date</th>
                    <th className="py-2 pr-4 font-medium">Rating</th>
                    <th className="py-2 pr-4 font-medium">State</th>
                    <th className="py-2 font-medium" />
                  </tr>
                </thead>
                <tbody>
                  {appraisals.data?.map((a) => (
                    <tr key={a.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">{a.employee_name}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{a.appraisal_date}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{a.final_rating ?? "—"}</td>
                      <td className="py-2 pr-4">
                        <StateBadge state={a.state} />
                      </td>
                      <td className="py-2 text-right">
                        {a.state === "draft" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-green-600 hover:text-green-700"
                            onClick={() => handleComplete(a.id)}
                          >
                            Complete
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-muted-foreground hover:text-destructive"
                          onClick={() => handleDelete(a.id)}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {appraisals.data?.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-muted-foreground">
                        No appraisals yet.
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
