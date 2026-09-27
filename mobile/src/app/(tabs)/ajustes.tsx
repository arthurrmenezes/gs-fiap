import Constants from 'expo-constants';
import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ScrollView, StyleSheet, Switch, Text, View } from 'react-native';

import { Banner, Button, Card, CardTitle, TextField } from '../../components/ui';
import { pingApi } from '../../services/api';
import { taxonomy } from '../../services/offline';
import { DEFAULT_SETTINGS, getSettings, saveSettings } from '../../services/storage';
import { colors, spacing, typography } from '../../theme';
import type { AppSettings } from '../../types';

type TestResult = 'idle' | 'testing' | 'ok' | 'fail';

export default function SettingsScreen() {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [test, setTest] = useState<TestResult>('idle');
  const [saved, setSaved] = useState(false);

  useFocusEffect(
    useCallback(() => {
      getSettings().then(setSettings);
    }, []),
  );

  function update(changes: Partial<AppSettings>) {
    setSettings({ ...settings, ...changes });
    setSaved(false);
    setTest('idle');
  }

  async function handleSave() {
    await saveSettings({ ...settings, apiUrl: settings.apiUrl.trim() });
    setSaved(true);
  }

  async function handleTest() {
    setTest('testing');
    setTest((await pingApi(settings.apiUrl)) ? 'ok' : 'fail');
  }

  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <Card>
        <CardTitle icon="server" title="Fonte de dados" />
        <View style={styles.switchRow}>
          <View style={{ flex: 1 }}>
            <Text style={typography.body}>Usar servidor (API)</Text>
            <Text style={typography.caption}>
              {settings.useApi
                ? 'As fichas são geradas pelo backend SpecRadar.'
                : 'As fichas são geradas com os dados embarcados no app (funciona sem internet).'}
            </Text>
          </View>
          <Switch
            value={settings.useApi}
            onValueChange={(useApi) => update({ useApi })}
            trackColor={{ true: colors.accent, false: colors.border }}
            thumbColor={colors.surface}
          />
        </View>

        {settings.useApi && (
          <>
            <TextField
              label="Endereço do servidor"
              value={settings.apiUrl}
              onChangeText={(apiUrl) => update({ apiUrl })}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="url"
              placeholder="http://192.168.0.10:8000"
            />
            <Text style={typography.caption}>
              Emulador: http://10.0.2.2:8000 · Celular: use o IP do computador na mesma rede
              Wi-Fi (ex.: http://192.168.0.10:8000).
            </Text>
            <Button
              title="Testar conexão"
              icon="pulse"
              variant="secondary"
              onPress={handleTest}
              loading={test === 'testing'}
            />
            {test === 'ok' && <Banner text="Servidor respondeu. Conexão OK!" />}
            {test === 'fail' && (
              <Banner
                tone="warning"
                text="Não foi possível conectar. Confira o endereço e se o backend está rodando. Enquanto isso, o app usa os dados offline."
              />
            )}
          </>
        )}

        <Button title={saved ? 'Salvo!' : 'Salvar ajustes'} icon="save" onPress={handleSave} />
      </Card>

      <Card>
        <CardTitle icon="information-circle" title="Sobre o SpecRadar" />
        <Text style={styles.paragraph}>
          Ferramenta de inteligência competitiva automotiva (desafio FIAP × Ford). Recebe marca,
          modelo, versão e uma lista livre de atributos e devolve uma ficha técnica sempre no
          mesmo formato, comparável entre veículos.
        </Text>
        <Text style={styles.paragraph}>
          Dados ausentes aparecem como “Não disponível” e valores suspeitos (ex.: preço fora da
          faixa esperada) são marcados como “Anomalia”.
        </Text>
        <InfoLine label="Versão do app" value={Constants.expoConfig?.version ?? '1.0.0'} />
        <InfoLine label="Atributos na taxonomia" value={String(taxonomy.length)} />
        <InfoLine label="Validação" value="Ford Ranger Raptor" />
      </Card>
    </ScrollView>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoLine}>
      <Text style={typography.caption}>{label}</Text>
      <Text style={[typography.body, { fontWeight: '600' }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.lg, gap: spacing.lg, paddingBottom: spacing.xxl },
  switchRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  paragraph: { ...typography.body, lineHeight: 22, color: colors.textMuted },
  infoLine: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: spacing.xs,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
});
