import { useMutation } from "@tanstack/react-query";
import { AppShell } from "@/components/AppShell";
import { SearchConsole } from "@/components/SearchConsole";
import { SpecSheet } from "@/components/SpecSheet";
import { ErrorState, InitialState, LoadingState } from "@/components/States";
import { VehicleSummary } from "@/components/VehicleSummary";
import { fetchSpecSheet } from "@/lib/api";
import type { SpecRequest, SpecSheet as SpecSheetData } from "@/types";

export default function App() {
  const mutation = useMutation<SpecSheetData, Error, SpecRequest>({
    mutationFn: fetchSpecSheet,
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <SearchConsole onSubmit={(req) => mutation.mutate(req)} loading={mutation.isPending} />

        {mutation.isIdle && <InitialState />}
        {mutation.isPending && <LoadingState />}
        {mutation.isError && <ErrorState error={mutation.error} />}
        {mutation.isSuccess && (
          <div className="space-y-5">
            <VehicleSummary sheet={mutation.data} />
            <SpecSheet sheet={mutation.data} />
          </div>
        )}
      </div>
    </AppShell>
  );
}
