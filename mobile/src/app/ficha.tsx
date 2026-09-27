import Ionicons from '@expo/vector-icons/Ionicons';
import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, SectionList, Share, StyleSheet, Text, View } from 'react-native';

import { SheetSummary, SpecRow } from '../components/spec';
import { Banner, Chip, EmptyState } from '../components/ui';
import { getHistoryEntry } from '../services/storage';
import { colors, spacing, typography } from '../theme';
import type { HistoryEntry, SpecField } from '../types';
import {
  countByStatus,
  formatDate,
  groupFields,
  modeLabel,
  sheetToText,
  vehicleSubtitle,
  vehicleTitle,
} from '../utils/format';

type Filter = 'all' | 'found' | 'missing' | 'alerts';

const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'Todos' },
  { key: 'found', label: 'Encontrados' },
  { key: 'missing', label: 'Não disponíveis' },
  { key: 'alerts', label: 'Alertas' },
];

function matchesFilter(field: SpecField, filter: Filter): boolean {
  if (filter === 'found') return field.status === 'OK';
  if (filter === 'missing') return field.status === 'NA';
  if (filter === 'alerts') return field.status !== 'OK' && field.status !== 'NA';
  return true;
}

export default function SheetScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [entry, setEntry] = useState<HistoryEntry | null | undefined>(undefined);
  const [filter, setFilter] = useState<Filter>('all');

  useEffect(() => {
    getHistoryEntry(id).then((found) => setEntry(found ?? null));
  }, [id]);

  const sections = useMemo(() => {
    if (!entry) return [];
    return groupFields(entry.sheet.fields.filter((f) => matchesFilter(f, filter)));
  }, [entry, filter]);

  if (entry === undefined) {
    return <ActivityIndicator style={{ marginTop: spacing.xxl }} color={colors.accent} />;
  }
  if (entry === null) {
    return (
      <EmptyState
        icon="document-outline"
        title="Ficha não encontrada"
        text="Ela pode ter sido removida do histórico."
      />
    );
  }

  const { sheet } = entry;
  const counts = countByStatus(sheet.fields);

  function share() {
    Share.share({ message: sheetToText(sheet) });
  }

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <Pressable onPress={share} hitSlop={12} accessibilityLabel="Compartilhar ficha">
              <Ionicons name="share-social" size={22} color={colors.textOnPrimary} />
            </Pressable>
          ),
        }}
      />
      <SectionList
        sections={sections}
        keyExtractor={(item) => item.attribute_id}
        stickySectionHeadersEnabled={false}
        contentContainerStyle={{ paddingBottom: spacing.xxl }}
        ListHeaderComponent={
          <View style={styles.header}>
            <View style={styles.vehicle}>
              <Text style={typography.title}>{vehicleTitle(sheet)}</Text>
              <Text style={typography.body}>{vehicleSubtitle(sheet)}</Text>
              <View style={styles.metaRow}>
                <Meta icon="cloud-done-outline" text={modeLabel(sheet.mode)} />
                <Meta icon="link-outline" text={`${sheet.source_count} fonte(s)`} />
                <Meta icon="calendar-outline" text={formatDate(sheet.generated_at)} />
              </View>
              <SheetSummary found={counts.found} missing={counts.missing} alerts={counts.alerts} />
            </View>

            {entry.notice && <Banner tone="warning" text={entry.notice} />}
            {sheet.source_count === 0 && (
              <Banner text="Nenhuma fonte com dados foi encontrada para este veículo. A ficha mantém o mesmo formato, com todos os campos marcados como “Não disponível”." />
            )}
            {sheet.unknown_attributes.length > 0 && (
              <Banner
                tone="warning"
                text={`Atributos não reconhecidos: ${sheet.unknown_attributes.join(', ')}. Tente outro nome (ex.: “potência”, “câmbio”).`}
              />
            )}

            <View style={styles.filters}>
              {FILTERS.map((f) => (
                <Chip
                  key={f.key}
                  label={f.label}
                  selected={filter === f.key}
                  onPress={() => setFilter(f.key)}
                />
              ))}
            </View>
          </View>
        }
        renderSectionHeader={({ section }) => (
          <Text style={styles.sectionHeader}>{section.title}</Text>
        )}
        renderItem={({ item }) => (
          <SpecRow
            field={item}
            onPress={() =>
              router.push({ pathname: '/atributo', params: { id, attr: item.attribute_id } })
            }
          />
        )}
        ListEmptyComponent={
          <EmptyState
            icon="funnel-outline"
            title="Nada neste filtro"
            text="Escolha outro filtro para ver os demais campos."
          />
        }
      />
    </>
  );
}

function Meta({ icon, text }: { icon: 'cloud-done-outline' | 'link-outline' | 'calendar-outline'; text: string }) {
  return (
    <View style={styles.meta}>
      <Ionicons name={icon} size={14} color={colors.textMuted} />
      <Text style={typography.caption}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { padding: spacing.lg, gap: spacing.md },
  vehicle: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.lg,
    gap: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  metaRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.md, marginBottom: spacing.xs },
  meta: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  filters: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  sectionHeader: {
    ...typography.label,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
  },
});
