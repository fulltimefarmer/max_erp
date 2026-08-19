import { create } from "zustand";

import type { Permissions, UserInfo } from "@/types/api";

interface DashboardState {
  permissions: Permissions | null;
  me: UserInfo | null;
  setPermissions: (permissions: Permissions | null) => void;
  setMe: (me: UserInfo | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  permissions: null,
  me: null,
  setPermissions: (permissions) => set({ permissions }),
  setMe: (me) => set({ me }),
}));
