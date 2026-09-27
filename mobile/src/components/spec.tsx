// Componentes específicos da ficha técnica: selo de status, linha e resumo.
import Ionicons from '@expo/vector-icons/Ionicons';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, statusMeta } from '../theme';
import type { SpecField, SpecStatus } from '../types';
import { formatField } from '../utils/format';
import type { IconName } from './ui';

export function StatusBadge({ status }: { status: SpecStatus }) {
  const meta = statusMeta[status];
  return (
    <View style={[styles.badge, { backgroundColor: meta.background }]}>
      <Ionicons name={meta.icon as IconName} size={13} color={meta.color} />
      <Text style={[styles.badgeText, { color: meta.color }]}>{meta.label}</Text>
    </View>
  );
}

export function SpecRow({ field, onPress }: { field: SpecField; onPress: () => void }) {
  const missing = field.status === 'NA';
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.row, pressed && { backgroundColor: colors.background }]}
    >
      <View style={styles.rowText}>
        <Text style={styles.rowName}>{field.name}</Text>
        <Text style={[styles.rowValue, missing && styles.rowValueMissing]}>
          {formatField(field)}
        </Text>
      </View>
      {!missing && <StatusBadge status={field.status} />}
      <Ionicons name="chevron-forward" size={18} color={colors.border} />
    </Pressable>
  );
}

interface SummaryProps {
  found: number;
  missing: number;
  alerts: number;
}

export function SheetSummary({ found, missing, alerts }: SummaryProps) {
  return (
    <View style={styles.summary}>
      <SummaryItem value={found} label="Encontrados" color={statusMeta.OK.color} />
      <SummaryItem value={missing} label="Não disponíveis" color={statusMeta.NA.color} />
      <SummaryItem value={alerts} label="Alertas" color={statusMeta.ANOMALY.color} />
    </View>
  );
}

function SummaryItem({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <View style={styles.summaryItem}>
      <Text style={[styles.summaryValue, { color }]}>{value}</Text>
      <Text style={styles.summaryLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.pill,
    alignSelf: 'flex-start',
  },
  badgeText: { fontSize: 12, fontWeight: '700' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    backgroundColor: colors.surface,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  rowText: { flex: 1, gap: 2 },
  rowName: { fontSize: 13, color: colors.textMuted },
  rowValue: { fontSize: 16, fontWeight: '600', color: colors.text },
  rowValueMissing: { fontWeight: '400', fontStyle: 'italic', color: colors.textMuted },
  summary: { flexDirection: 'row', gap: spacing.sm },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.background,
  },
  summaryValue: { fontSize: 24, fontWeight: '800' },
  summaryLabel: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
});
