// Persistência local com AsyncStorage: histórico de fichas e configurações.
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { AppSettings, HistoryEntry } from '../types';

const HISTORY_KEY = '@specradar/history';
const SETTINGS_KEY = '@specradar/settings';
const MAX_HISTORY = 30;

// 10.0.2.2 é o "localhost" do computador visto de dentro do emulador Android.
export const DEFAULT_SETTINGS: AppSettings = {
  useApi: false,
  apiUrl: 'http://10.0.2.2:8000',
};

export async function getHistory(): Promise<HistoryEntry[]> {
  const raw = await AsyncStorage.getItem(HISTORY_KEY);
  return raw ? (JSON.parse(raw) as HistoryEntry[]) : [];
}

export async function getHistoryEntry(id: string): Promise<HistoryEntry | undefined> {
  const history = await getHistory();
  return history.find((entry) => entry.id === id);
}

export async function addHistoryEntry(entry: HistoryEntry): Promise<void> {
  const history = await getHistory();
  const updated = [entry, ...history].slice(0, MAX_HISTORY);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

export async function removeHistoryEntry(id: string): Promise<void> {
  const history = await getHistory();
  await AsyncStorage.setItem(
    HISTORY_KEY,
    JSON.stringify(history.filter((entry) => entry.id !== id)),
  );
}

export async function clearHistory(): Promise<void> {
  await AsyncStorage.removeItem(HISTORY_KEY);
}

export async function getSettings(): Promise<AppSettings> {
  const raw = await AsyncStorage.getItem(SETTINGS_KEY);
  return raw ? { ...DEFAULT_SETTINGS, ...(JSON.parse(raw) as AppSettings) } : DEFAULT_SETTINGS;
}

export async function saveSettings(settings: AppSettings): Promise<void> {
  await AsyncStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}
