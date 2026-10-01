// 统一请求封装：只请求同源 /api，禁止硬编码 localhost。
// 当前演示身份保存在 localStorage，通过 x-user-id 切换本地账号（配合后端中间件）。
const ACTOR_KEY = "fire-inspect-actor";

export function getActorId(): number {
  const raw = localStorage.getItem(ACTOR_KEY);
  return raw ? Number(raw) : 3;
}

export function setActorId(id: number) {
  localStorage.setItem(ACTOR_KEY, String(id));
}

export interface ApiErrorBody {
  code: string;
  message: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-user-id": String(getActorId()),
    ...(options.headers as Record<string, string> | undefined)
  };
  const res = await fetch(`/api${path}`, { ...options, headers });
  if (!res.ok) {
    let body: { detail?: ApiErrorBody | string } | ApiErrorBody | null = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    const detail = (body as { detail?: ApiErrorBody })?.detail;
    const code = typeof detail === "object" && detail ? detail.code : "WRITE_FAILED";
    const message =
      (typeof detail === "object" && detail && detail.message) ||
      (typeof body === "object" && body && "message" in body && (body as ApiErrorBody).message) ||
      `请求失败（${res.status}）`;
    const error = new Error(message) as Error & { code: string; status: number };
    error.code = code;
    error.status = res.status;
    throw error;
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, payload?: unknown) =>
    request<T>(path, { method: "POST", body: payload === undefined ? undefined : JSON.stringify(payload) }),
  patch: <T>(path: string, payload?: unknown) =>
    request<T>(path, { method: "PATCH", body: payload === undefined ? undefined : JSON.stringify(payload) })
};
