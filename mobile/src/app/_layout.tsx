// Navegação raiz: as abas (Pesquisar / Histórico / Ajustes) + telas empilhadas
// da ficha técnica e do detalhe de cada atributo.
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

import { colors } from '../theme';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.primary },
          headerTintColor: colors.textOnPrimary,
          headerTitleStyle: { fontWeight: '700' },
          contentStyle: { backgroundColor: colors.background },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="ficha" options={{ title: 'Ficha técnica' }} />
        <Stack.Screen name="atributo" options={{ title: 'Detalhe do atributo' }} />
      </Stack>
    </>
  );
}
