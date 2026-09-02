import { motion } from "framer-motion";
import { useMemo } from "react";
import { SpecRow } from "@/components/SpecRow";
import { Card } from "@/components/ui/Card";
import { groupMeta } from "@/lib/domain";
import type { SpecField, SpecSheet as SpecSheetData } from "@/types";

interface GroupedSection {
  key: string;
  label: string;
  order: number;
  icon: ReturnType<typeof groupMeta>["icon"];
  fields: SpecField[];
}

function groupFields(fields: SpecField[]): GroupedSection[] {
  const map = new Map<string, SpecField[]>();
  for (const f of fields) {
    const arr = map.get(f.group) ?? [];
    arr.push(f);
    map.set(f.group, arr);
  }
  return [...map.entries()]
    .map(([key, fs]) => {
      const meta = groupMeta(key);
      return { key, label: meta.label, order: meta.order, icon: meta.icon, fields: fs };
    })
    .sort((a, b) => a.order - b.order);
}

export function SpecSheet({ sheet }: { sheet: SpecSheetData }) {
  const sections = useMemo(() => groupFields(sheet.fields), [sheet.fields]);

  return (
    <div className="space-y-5">
      {sections.map((section, idx) => (
        <motion.div
          key={section.key}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: Math.min(idx * 0.04, 0.3), ease: [0.16, 1, 0.3, 1] }}
        >
          <Card className="overflow-hidden">
            <SectionHeader section={section} />
            <div className="divide-y divide-graphite-100">
              {section.fields.map((field) => (
                <SpecRow key={field.attribute_id} field={field} />
              ))}
            </div>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}

function SectionHeader({ section }: { section: GroupedSection }) {
  const Icon = section.icon;
  const filled = section.fields.filter((f) => f.status !== "NA").length;
  return (
    <div className="flex items-center justify-between border-b border-graphite-100 bg-graphite-25 px-6 py-3">
      <div className="flex items-center gap-2.5">
        <Icon className="h-[18px] w-[18px] text-ford-500" />
        <h3 className="text-sm font-bold tracking-brand text-graphite-900">{section.label}</h3>
      </div>
      <span className="tnum text-xs font-medium text-graphite-400">
        {filled}/{section.fields.length}
      </span>
    </div>
  );
}
