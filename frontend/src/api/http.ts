// 统一请求封装：前端代码只请求 /api，禁止硬编码 localhost（由 Nginx 反代到后端）。
import { ERROR_MESSAGES } from "../constants/errorMessages";

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

const DEFAULT_HEADERS: Record<string, string> = {
  "Content-Type": "application/json",
  // 本地演示身份；接入登录后替换为 JWT。
  "x-user-id": "100",
  "x-role": "SUPERVISOR"
};

export class ApiRequestError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown>;

  constructor(code: string, message: string, status: number,
              details?: Record<string, unknown>) {
    super(message);
    this.name = "ApiRequestError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`/api${path}`, {
      ...options,
      headers: { ...DEFAULT_HEADERS, ...(options.headers ?? {}) }
    });
  } catch {
    throw new ApiRequestError(
      "INTERNAL_ERROR",
      ERROR_MESSAGES.INTERNAL_ERROR,
      0
    );
  }

  if (!res.ok) {
    let body: ApiError = { code: "INTERNAL_ERROR", message: ERROR_MESSAGES.INTERNAL_ERROR };
    try {
      body = await res.json();
    } catch {
      // 非 JSON 错误响应时使用默认消息
    }
    throw new ApiRequestError(
      body.code ?? "INTERNAL_ERROR",
      body.message ?? ERROR_MESSAGES.INTERNAL_ERROR,
      res.status,
      body.details
    );
  }
  return (await res.json()) as T;
}

export const http = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" })
};
