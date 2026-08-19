export interface RoleInfo {
  id: number;
  name: string;
  description: string | null;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  roles: RoleInfo[];
}

export interface MenuItem {
  id: number;
  name: string;
  code: string;
  parent_id: number | null;
  sequence: number;
  icon: string | null;
  active: boolean;
  role_names: string[];
}

export interface PageItem {
  id: number;
  name: string;
  code: string;
  route: string;
  active: boolean;
  role_names: string[];
}

export interface ModelAccessSummary {
  model: string;
  create: boolean;
  read: boolean;
  write: boolean;
  unlink: boolean;
}

export interface Permissions {
  menus: MenuItem[];
  pages: PageItem[];
  model_accesses: ModelAccessSummary[];
}

export interface Employee {
  id: number;
  name: string;
  work_email: string | null;
  phone: string | null;
  hire_date: string | null;
  job_id: number | null;
  department_id: number | null;
  manager_id: number | null;
  user_id: number | null;
  active: boolean;
  created_at: string;
  job_name: string | null;
  department_name: string | null;
  manager_name: string | null;
}

export interface Department {
  id: number;
  name: string;
  code: string | null;
  parent_id: number | null;
  active: boolean;
  created_at: string;
}

export interface JobPosition {
  id: number;
  name: string;
  code: string | null;
  department_id: number | null;
  active: boolean;
  created_at: string;
}

export interface ModelAccessRecord {
  id: number;
  model: string;
  role_id: number;
  role_name: string;
  perm_create: boolean;
  perm_read: boolean;
  perm_write: boolean;
  perm_unlink: boolean;
  created_at: string;
}
