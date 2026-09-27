// Identidade visual do SpecRadar: todas as cores, espaçamentos e tamanhos de
// fonte do app vêm daqui. Nenhuma tela deve usar cor "solta".
import type { SpecStatus } from './types';

export const colors = {
  primary: '#0B2545', // azul-marinho (marca)
  primaryLight: '#13315C',
  accent: '#1F7AE0', // azul de ação (botões, links)
  accentSoft: '#E8F1FC',
  accentBorder: '#B9D5F7',
  background: '#F3F5F9',
  surface: '#FFFFFF',
  border: '#DDE3EC',
  text: '#16202E',
  textMuted: '#5B6778',
  textOnPrimary: '#FFFFFF',
  textOnPrimaryMuted: '#C9D6EA',
  danger: '#C62828',
  success: '#1E8E4E',
  warning: '#B26A00',
  warningSoft: '#FFF3DC',
  warningBorder: '#F0C36D',
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32 };

export const radius = { sm: 6, md: 10, lg: 16, pill: 999 };

export const typography = {
  title: { fontSize: 22, fontWeight: '700' as const, color: colors.text },
  subtitle: { fontSize: 17, fontWeight: '600' as const, color: colors.text },
  body: { fontSize: 15, color: colors.text },
  caption: { fontSize: 13, color: colors.textMuted },
  label: {
    fontSize: 12,
    fontWeight: '700' as const,
    color: colors.textMuted,
    letterSpacing: 0.6,
    textTransform: 'uppercase' as const,
  },
};

// Cor, rótulo e explicação de cada status da ficha.
export const statusMeta: Record<
  SpecStatus,
  { label: string; color: string; background: string; icon: string; description: string }
> = {
  OK: {
    label: 'Encontrado',
    color: '#1E8E4E',
    background: '#E3F4EA',
    icon: 'checkmark-circle',
    description: 'Valor encontrado e confirmado no texto da fonte.',
  },
  NA: {
    label: 'Não disponível',
    color: '#5B6778',
    background: '#ECEFF3',
    icon: 'remove-circle',
    description:
      'Nenhuma fonte trouxe este dado. O campo fica vazio de propósito: o app nunca inventa um valor.',
  },
  ANOMALY: {
    label: 'Anomalia',
    color: '#C62828',
    background: '#FDE7E7',
    icon: 'warning',
    description:
      'O valor foi encontrado, mas está fora da faixa esperada para este tipo de veículo. Confira antes de usar.',
  },
  CONFLICT: {
    label: 'Conflito',
    color: '#7B3FC4',
    background: '#F1E9FB',
    icon: 'git-compare',
    description: 'As fontes trazem valores diferentes. Os dois valores foram mantidos para análise.',
  },
  LOW_CONFIDENCE: {
    label: 'Baixa confiança',
    color: '#B26A00',
    background: '#FFF3DC',
    icon: 'help-circle',
    description: 'O valor veio de uma fonte menos confiável ou com pouca certeza na leitura.',
  },
};
