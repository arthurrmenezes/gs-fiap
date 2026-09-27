import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, Linking, ScrollView, StyleSheet, Text, View } from 'react-native';

import { StatusBadge } from '../components/spec';
import { Button, Card, CardTitle, EmptyState } from '../components/ui';
import { getHistoryEntry } from '../services/storage';
import { colors, radius, spacing, statusMeta, typography } from '../theme';
import type { SpecField } from '../types';
import {
  domainOf,
  formatField,
  formatValue,
  groupLabel,
  NOT_AVAILABLE,
  SUBFIELD_LABELS,
  tierLabel,
} from '../utils/format';

export default function AttributeScreen() {
  const { id, attr } = useLocalSearchParams<{ id: string; attr: string }>();
  const [field, setField] = useState<SpecField | null | undefined>(undefined);

  useEffect(() => {
    getHistoryEntry(id).then((entry) =>
      setField(entry?.sheet.fields.find((f) => f.attribute_id === attr) ?? null),
    );
  }, [id, attr]);

  if (field === undefined) {
    return <ActivityIndicator style={{ marginTop: spacing.xxl }} color={colors.accent} />;
  }
  if (field === null) {
    return <EmptyState icon="help-circle-outline" title="Atributo não encontrado" text="" />;
  }

  const meta = statusMeta[field.status];
  const missing = field.status === 'NA';
  const subfields =
    field.value && typeof field.value === 'object' && !Array.isArray(field.value)
      ? Object.entries(field.value)
      : [];
  const confidence = Math.round(field.confidence * 100);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Card>
        <Text style={typography.label}>{groupLabel(field.group)}</Text>
        <Text style={typography.title}>{field.name}</Text>
        <Text style={[styles.value, missing && styles.valueMissing]}>{formatField(field)}</Text>
        <StatusBadge status={field.status} />
        <Text style={[styles.statusText, { borderLeftColor: meta.color }]}>{meta.description}</Text>
        {field.note && field.status !== 'OK' && (
          <Text style={typography.caption}>Detalhe técnico: {field.note}</Text>
        )}
      </Card>

      {subfields.length > 0 && (
        <Card>
          <CardTitle icon="construct" title="Valor decomposto" />
          {subfields.map(([key, v]) => (
            <InfoRow
              key={key}
              label={SUBFIELD_LABELS[key] ?? key}
              value={typeof v === 'boolean' ? (v ? 'Sim' : 'Não') : String(v)}
            />
          ))}
        </Card>
      )}

      {field.status === 'CONFLICT' && field.alternatives.length > 0 && (
        <Card>
          <CardTitle icon="git-compare" title="Valores em conflito" />
          {field.alternatives.map((alt, i) => (
            <InfoRow key={i} label={`Fonte ${i + 1}`} value={formatValue(alt, field.unit)} />
          ))}
        </Card>
      )}

      <Card>
        <CardTitle icon="document-text" title="Origem do dado" />
        {missing ? (
          <Text style={typography.body}>
            Nenhuma das fontes consultadas trouxe este atributo, por isso ele aparece como “
            {NOT_AVAILABLE}”.
          </Text>
        ) : (
          <>
            <InfoRow label="Texto original" value={field.value_raw ?? NOT_AVAILABLE} />
            <InfoRow label="Fonte" value={domainOf(field.source_url)} />
            <InfoRow label="Confiabilidade da fonte" value={tierLabel(field.source_tier)} />
            <View style={{ gap: spacing.xs }}>
              <Text style={styles.infoLabel}>Confiança da leitura: {confidence}%</Text>
              <View style={styles.barTrack}>
                <View style={[styles.barFill, { width: `${confidence}%` }]} />
              </View>
            </View>
            {field.evidence_snippet && (
              <View style={{ gap: spacing.xs }}>
                <Text style={styles.infoLabel}>Trecho da fonte (evidência)</Text>
                <Text style={styles.quote}>“{field.evidence_snippet}”</Text>
              </View>
            )}
            {field.source_url && (
              <Button
                title="Abrir fonte"
                icon="open-outline"
                variant="secondary"
                onPress={() => Linking.openURL(field.source_url!)}
              />
            )}
          </>
        )}
      </Card>
    </ScrollView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.lg, gap: spacing.lg, paddingBottom: spacing.xxl },
  value: { fontSize: 26, fontWeight: '800', color: colors.primary },
  valueMissing: { fontSize: 20, fontWeight: '400', fontStyle: 'italic', color: colors.textMuted },
  statusText: {
    ...typography.body,
    color: colors.textMuted,
    borderLeftWidth: 3,
    paddingLeft: spacing.md,
    lineHeight: 21,
  },
  infoRow: { gap: 2 },
  infoLabel: { fontSize: 13, color: colors.textMuted },
  infoValue: { fontSize: 16, color: colors.text, fontWeight: '500' },
  barTrack: { height: 8, borderRadius: radius.pill, backgroundColor: colors.background },
  barFill: { height: 8, borderRadius: radius.pill, backgroundColor: colors.accent },
  quote: {
    fontSize: 15,
    fontStyle: 'italic',
    color: colors.text,
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: radius.md,
    lineHeight: 21,
  },
});
