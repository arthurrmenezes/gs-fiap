import type { SpecRequest, SpecSheet, TaxonomyResponse } from "@/types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!resp.ok) {
    let detail = `${resp.status} ${resp.statusText}`;
    try {
      const body = await resp.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* keep the status-line detail */
    }
    throw new ApiError(detail, resp.status);
  }
  return resp.json() as Promise<T>;
}

export function fetchSpecSheet(req: SpecRequest): Promise<SpecSheet> {
  return request<SpecSheet>("/spec", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function fetchTaxonomy(): Promise<TaxonomyResponse> {
  return request<TaxonomyResponse>("/taxonomy");
}
