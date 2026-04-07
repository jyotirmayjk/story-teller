const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiBaseUrl = rawApiBaseUrl.replace(/\/$/, '');
export const wsBaseUrl = (
  import.meta.env.VITE_WS_BASE_URL ||
  apiBaseUrl.replace(/^http/, 'ws')
).replace(/\/$/, '');

type JsonEnvelope<T> = T | { data: T };

const unwrap = <T>(payload: JsonEnvelope<T>): T => {
  if (typeof payload === 'object' && payload !== null && 'data' in payload) {
    return (payload as { data: T }).data;
  }
  return payload as T;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const json = await response.json();
      message = json.detail || json.message || message;
    } catch {
      // No-op.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const json = (await response.json()) as JsonEnvelope<T>;
  return unwrap(json);
}

export const apiClient = {
  get: <T>(path: string, token?: string | null) =>
    request<T>(path, { method: 'GET' }, token),
  post: <T>(path: string, body?: unknown, token?: string | null) =>
    request<T>(
      path,
      {
        method: 'POST',
        body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
      },
      token,
    ),
  patch: <T>(path: string, body?: unknown, token?: string | null) =>
    request<T>(
      path,
      {
        method: 'PATCH',
        body: JSON.stringify(body ?? {}),
      },
      token,
    ),
};
