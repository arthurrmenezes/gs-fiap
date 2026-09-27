// Tela "Histórico": fichas geradas anteriormente, salvas no aparelho.
import Ionicons from '@expo/vector-icons/Ionicons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { Button, EmptyState } from '../../components/ui';
import { clearHistory, getHistory, removeHistoryEntry } from '../../services/storage';
import { colors, radius, spacing, typography } from '../../theme';
import type { HistoryEntry } from '../../types';
import { countByStatus, formatDate, vehicleSubtitle, vehicleTitle } from '../../utils/format';

export default function HistoryScreen() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  // Recarrega sempre que a aba ganha foco (ex.: depois de gerar uma ficha).
  useFocusEffect(
    useCallback(() => {
      getHistory().then(setHistory);
    }, []),
  );

  async function remove(id: string) {
    await removeHistoryEntry(id);
    setHistory(await getHistory());
  }

  function confirmClear() {
    Alert.alert('Limpar histórico', 'Apagar todas as fichas salvas neste aparelho?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Apagar',
        style: 'destructive',
        onPress: async () => {
          await clearHistory();
          setHistory([]);
        },
      },
    ]);
  }

  return (
    <FlatList
      data={history}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.list}
      ListEmptyComponent={
        <EmptyState
          icon="time-outline"
          title="Nenhuma ficha ainda"
          text="As fichas que você gerar na aba Pesquisar aparecem aqui, mesmo sem internet."
        />
      }
      ListFooterComponent={
        history.length > 0 ? (
          <Button title="Limpar histórico" icon="trash" variant="danger" onPress={confirmClear} />
        ) : null
      }
      renderItem={({ item }) => {
        const counts = countByStatus(item.sheet.fields);
        return (
          <Pressable
            style={({ pressed }) => [styles.item, pressed && { opacity: 0.85 }]}
            onPress={() => router.push({ pathname: '/ficha', params: { id: item.id } })}
          >
            <View style={styles.icon}>
              <Ionicons name="car-sport" size={22} color={colors.accent} />
            </View>
            <View style={{ flex: 1, gap: 2 }}>
              <Text style={typography.subtitle}>{vehicleTitle(item.sheet)}</Text>
              <Text style={typography.caption}>{vehicleSubtitle(item.sheet)}</Text>
              <Text style={typography.caption}>
                {formatDate(item.createdAt)} · {counts.found}/{counts.total} encontrados
                {counts.alerts > 0 ? ` · ${counts.alerts} alerta(s)` : ''}
              </Text>
            </View>
            <Pressable
              hitSlop={12}
              onPress={() => remove(item.id)}
              accessibilityLabel="Remover do histórico"
            >
              <Ionicons name="trash-outline" size={20} color={colors.textMuted} />
            </Pressable>
          </Pressable>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  list: { padding: spacing.lg, gap: spacing.md, flexGrow: 1 },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  icon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
