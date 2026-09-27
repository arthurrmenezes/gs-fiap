import { router } from 'expo-router';
import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { Button, Card, CardTitle, Chip, TextField } from '../../components/ui';
import { fetchSpecSheet } from '../../services/api';
import { taxonomy } from '../../services/offline';
import { addHistoryEntry, getSettings } from '../../services/storage';
import { colors, spacing, typography } from '../../theme';
import type { SpecRequest } from '../../types';

type Errors = Partial<Record<'make' | 'model' | 'version' | 'year', string>>;

const SUGGESTIONS = taxonomy
  .filter((attr, i) => taxonomy.findIndex((a) => a.group === attr.group) === i)
  .map((attr) => attr.name);

const RAPTOR_EXAMPLE = {
  make: 'Ford',
  model: 'Ranger Raptor',
  version: 'Raptor 3.0 V6',
  year: '2026',
  attributes: [
    'Potência',
    'Torque',
    'Configuração do motor',
    'Transmissão',
    'Tração',
    'Modos de condução',
    'Pneus',
    'Faróis',
    'Preço',
    'Emissão de CO2',
  ],
};

export default function SearchScreen() {
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [version, setVersion] = useState('');
  const [year, setYear] = useState('');
  const [attributeInput, setAttributeInput] = useState('');
  const [attributes, setAttributes] = useState<string[]>([]);
  const [errors, setErrors] = useState<Errors>({});
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);

  function addAttribute(label: string) {
    const value = label.trim();
    if (!value) return;
    const exists = attributes.some((a) => a.toLowerCase() === value.toLowerCase());
    if (!exists) setAttributes([...attributes, value]);
    setAttributeInput('');
  }

  function removeAttribute(label: string) {
    setAttributes(attributes.filter((a) => a !== label));
  }

  function fillExample() {
    setMake(RAPTOR_EXAMPLE.make);
    setModel(RAPTOR_EXAMPLE.model);
    setVersion(RAPTOR_EXAMPLE.version);
    setYear(RAPTOR_EXAMPLE.year);
    setAttributes(RAPTOR_EXAMPLE.attributes);
    setErrors({});
  }

  function clearForm() {
    setMake('');
    setModel('');
    setVersion('');
    setYear('');
    setAttributes([]);
    setAttributeInput('');
    setErrors({});
  }

  function validate(): Errors {
    const found: Errors = {};
    if (!make.trim()) found.make = 'Informe a marca.';
    if (!model.trim()) found.model = 'Informe o modelo.';
    if (!version.trim()) found.version = 'Informe a versão.';
    const yearNumber = Number(year);
    if (year && (!Number.isInteger(yearNumber) || yearNumber < 1990 || yearNumber > 2100)) {
      found.year = 'Ano inválido (ex.: 2026).';
    }
    return found;
  }

  async function handleSubmit() {
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length > 0) return;

    const allAttributes = attributeInput.trim() ? [...attributes, attributeInput] : attributes;
    const request: SpecRequest = {
      make: make.trim(),
      model: model.trim(),
      version: version.trim(),
      year: year ? Number(year) : null,
      attributes: allAttributes,
    };

    setLoading(true);
    try {
      const settings = await getSettings();
      const { sheet, notice } = await fetchSpecSheet(request, settings);
      const id = String(Date.now());
      await addHistoryEntry({ id, createdAt: new Date().toISOString(), request, sheet, notice });
      router.push({ pathname: '/ficha', params: { id } });
    } finally {
      setLoading(false);
    }
  }

  const suggestions = (showAll ? taxonomy.map((a) => a.name) : SUGGESTIONS).filter(
    (name) => !attributes.includes(name),
  );

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <View style={styles.hero}>
          <Text style={styles.heroTitle}>Ficha técnica padronizada</Text>
          <Text style={styles.heroText}>
            Informe o veículo e os atributos que deseja comparar. A ficha sai sempre no mesmo
            formato, para qualquer marca.
          </Text>
        </View>

        <Card>
          <CardTitle icon="car-sport" title="Veículo" />
          <TextField
            label="Marca *"
            placeholder="Ex.: Ford"
            value={make}
            onChangeText={setMake}
            error={errors.make}
          />
          <TextField
            label="Modelo *"
            placeholder="Ex.: Ranger Raptor"
            value={model}
            onChangeText={setModel}
            error={errors.model}
          />
          <View style={styles.row}>
            <View style={{ flex: 2 }}>
              <TextField
                label="Versão *"
                placeholder="Ex.: Raptor 3.0 V6"
                value={version}
                onChangeText={setVersion}
                error={errors.version}
              />
            </View>
            <View style={{ flex: 1 }}>
              <TextField
                label="Ano"
                placeholder="Ex.: 2026"
                keyboardType="number-pad"
                maxLength={4}
                value={year}
                onChangeText={setYear}
                error={errors.year}
              />
            </View>
          </View>
        </Card>

        <Card>
          <CardTitle icon="list" title="Atributos" />
          <Text style={typography.caption}>
            Digite livremente (ex.: “cavalos”, “câmbio”, “tração 4x4”) ou toque nas sugestões.
            Deixe vazio para gerar a ficha completa ({taxonomy.length} atributos).
          </Text>
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <TextField
                label="Novo atributo"
                placeholder="Ex.: potência"
                value={attributeInput}
                onChangeText={setAttributeInput}
                onSubmitEditing={() => addAttribute(attributeInput)}
                returnKeyType="done"
                submitBehavior="submit"
              />
            </View>
            <Button
              title="Adicionar"
              icon="add"
              variant="secondary"
              onPress={() => addAttribute(attributeInput)}
              style={styles.addButton}
            />
          </View>

          {attributes.length > 0 && (
            <View>
              <Text style={styles.sectionLabel}>Selecionados ({attributes.length})</Text>
              <View style={styles.chips}>
                {attributes.map((label) => (
                  <Chip
                    key={label}
                    label={label}
                    selected
                    icon="close"
                    onPress={() => removeAttribute(label)}
                  />
                ))}
              </View>
            </View>
          )}

          <View>
            <Text style={styles.sectionLabel}>
              {showAll ? 'Todos os atributos' : 'Sugestões'}
            </Text>
            <View style={styles.chips}>
              {suggestions.map((name) => (
                <Chip key={name} label={name} icon="add" onPress={() => addAttribute(name)} />
              ))}
            </View>
            <Button
              title={showAll ? 'Mostrar menos' : 'Ver todos os atributos'}
              variant="ghost"
              onPress={() => setShowAll(!showAll)}
            />
          </View>
        </Card>

        <Button title="Gerar ficha" icon="document-text" onPress={handleSubmit} loading={loading} />
        <View style={styles.row}>
          <Button
            title="Exemplo: Raptor"
            icon="flash"
            variant="secondary"
            onPress={fillExample}
            style={{ flex: 1 }}
          />
          <Button
            title="Limpar"
            icon="refresh"
            variant="ghost"
            onPress={clearForm}
            style={{ flex: 1 }}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.lg, gap: spacing.lg, paddingBottom: spacing.xxl },
  hero: {
    backgroundColor: colors.primaryLight,
    borderRadius: 16,
    padding: spacing.lg,
    gap: spacing.xs,
  },
  heroTitle: { fontSize: 20, fontWeight: '700', color: colors.textOnPrimary },
  heroText: { fontSize: 14, color: colors.textOnPrimaryMuted, lineHeight: 20 },
  row: { flexDirection: 'row', gap: spacing.md, alignItems: 'flex-start' },
  addButton: { marginTop: 22 },
  sectionLabel: { ...typography.label, marginBottom: spacing.sm },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
});
