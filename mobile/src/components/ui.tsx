// Componentes básicos reutilizados em todas as telas (botão, campo, card...).
import Ionicons from '@expo/vector-icons/Ionicons';
import type { ComponentProps, ReactNode } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextInputProps,
  type ViewStyle,
} from 'react-native';

import { colors, radius, spacing, typography } from '../theme';

export type IconName = ComponentProps<typeof Ionicons>['name'];

// ---------------------------------------------------------------- Button
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  icon?: IconName;
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  icon,
  loading = false,
  disabled = false,
  style,
}: ButtonProps) {
  const palette = buttonPalette[variant];
  const isDisabled = disabled || loading;
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={isDisabled}
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: palette.bg, borderColor: palette.border },
        pressed && { opacity: 0.8 },
        isDisabled && { opacity: 0.5 },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={palette.fg} />
      ) : (
        <>
          {icon && <Ionicons name={icon} size={18} color={palette.fg} />}
          <Text style={[styles.buttonText, { color: palette.fg }]}>{title}</Text>
        </>
      )}
    </Pressable>
  );
}

const buttonPalette: Record<ButtonVariant, { bg: string; fg: string; border: string }> = {
  primary: { bg: colors.accent, fg: colors.textOnPrimary, border: colors.accent },
  secondary: { bg: colors.surface, fg: colors.accent, border: colors.accent },
  ghost: { bg: 'transparent', fg: colors.accent, border: 'transparent' },
  danger: { bg: colors.surface, fg: colors.danger, border: colors.danger },
};

// ---------------------------------------------------------------- TextField
interface TextFieldProps extends TextInputProps {
  label: string;
  error?: string;
}

export function TextField({ label, error, style, ...props }: TextFieldProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        placeholderTextColor={colors.textMuted}
        style={[styles.input, error ? { borderColor: colors.danger } : null, style]}
        {...props}
      />
      {error ? <Text style={styles.errorText}>{error}</Text> : null}
    </View>
  );
}

// ---------------------------------------------------------------- Card
export function Card({ children, style }: { children: ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function CardTitle({ icon, title }: { icon: IconName; title: string }) {
  return (
    <View style={styles.cardTitle}>
      <Ionicons name={icon} size={18} color={colors.primary} />
      <Text style={typography.subtitle}>{title}</Text>
    </View>
  );
}

// ---------------------------------------------------------------- Chip
interface ChipProps {
  label: string;
  onPress?: () => void;
  selected?: boolean;
  icon?: IconName;
}

export function Chip({ label, onPress, selected = false, icon }: ChipProps) {
  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.chip,
        selected && { backgroundColor: colors.primary, borderColor: colors.primary },
      ]}
    >
      <Text style={[styles.chipText, selected && { color: colors.textOnPrimary }]}>{label}</Text>
      {icon && (
        <Ionicons
          name={icon}
          size={14}
          color={selected ? colors.textOnPrimary : colors.textMuted}
        />
      )}
    </Pressable>
  );
}

// ---------------------------------------------------------------- Banner
type BannerTone = 'info' | 'warning';

export function Banner({ tone = 'info', text }: { tone?: BannerTone; text: string }) {
  const isWarning = tone === 'warning';
  return (
    <View
      style={[
        styles.banner,
        isWarning
          ? { backgroundColor: colors.warningSoft, borderColor: colors.warningBorder }
          : { backgroundColor: colors.accentSoft, borderColor: colors.accentBorder },
      ]}
    >
      <Ionicons
        name={isWarning ? 'warning-outline' : 'information-circle-outline'}
        size={20}
        color={isWarning ? colors.warning : colors.accent}
      />
      <Text style={styles.bannerText}>{text}</Text>
    </View>
  );
}

// ---------------------------------------------------------------- EmptyState
export function EmptyState({ icon, title, text }: { icon: IconName; title: string; text: string }) {
  return (
    <View style={styles.empty}>
      <View style={styles.emptyIcon}>
        <Ionicons name={icon} size={36} color={colors.accent} />
      </View>
      <Text style={[typography.subtitle, { textAlign: 'center' }]}>{title}</Text>
      <Text style={[typography.caption, { textAlign: 'center' }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 48,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 1.5,
  },
  buttonText: { fontSize: 16, fontWeight: '600' },
  field: { gap: spacing.xs },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: colors.text },
  input: {
    minHeight: 48,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  errorText: { fontSize: 13, color: colors.danger },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.lg,
    gap: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: 7,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipText: { fontSize: 14, color: colors.text },
  banner: {
    flexDirection: 'row',
    gap: spacing.sm,
    padding: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
    alignItems: 'flex-start',
  },
  bannerText: { flex: 1, fontSize: 14, color: colors.text, lineHeight: 20 },
  empty: { alignItems: 'center', gap: spacing.sm, padding: spacing.xxl },
  emptyIcon: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
});
