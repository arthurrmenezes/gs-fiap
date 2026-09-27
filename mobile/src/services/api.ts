// Comunicação com o backend (FastAPI). Se o servidor não responder, o app
// usa os dados offline e avisa o usuário — assim nenhum fluxo termina em erro.
import type { AppSettings, SpecRequest, SpecSheet } from '../types';
import { buildOfflineSheet } from './offline';

const REQUEST_TIMEOUT_MS = 60_000; // a busca ao vivo com IA pode demorar
const PING_TIMEOUT_MS = 5_000;

function cleanUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export interface SpecResult {
  sheet: SpecSheet;
  notice?: string;
}

export async function fetchSpecSheet(
  request: SpecRequest,
  settings: AppSettings,
): Promise<SpecResult> {
  if (!settings.useApi) {
    return { sheet: buildOfflineSheet(request) };
  }

  try {
    const response = await fetchWithTimeout(
      `${cleanUrl(settings.apiUrl)}/api/spec`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      },
      REQUEST_TIMEOUT_MS,
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { sheet: (await response.json()) as SpecSheet };
  } catch (error) {
    console.warn('API indisponível, usando dados offline:', error);
    return {
      sheet: buildOfflineSheet(request),
      notice: 'Não foi possível conectar ao servidor. Mostrando os dados offline do app.',
    };
  }
}

// Usado na tela de Ajustes para testar a URL do servidor.
export async function pingApi(apiUrl: string): Promise<boolean> {
  try {
    const response = await fetchWithTimeout(`${cleanUrl(apiUrl)}/api/health`, {}, PING_TIMEOUT_MS);
    return response.ok;
  } catch {
    return false;
  }
}
