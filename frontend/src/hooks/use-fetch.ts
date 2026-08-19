"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";

import { fetchBackend } from "@/lib/api";

export function useFetch<T>(path: string | null) {
  const { data: session } = useSession();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(path));
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = () => setRefreshKey((key) => key + 1);

  useEffect(() => {
    if (!path || !session?.accessToken) {
      return;
    }

    let active = true;
    setLoading(true);
    setError(null);

    fetchBackend<T>(path, session.accessToken)
      .then((result) => {
        if (active) setData(result);
      })
      .catch((err: Error) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [path, session?.accessToken, refreshKey]);

  return { data, loading, error, refresh };
}
