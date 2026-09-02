import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface FieldProps {
  label: string;
  hint?: string;
}

export const Input = forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement> & FieldProps
>(({ className, label, hint, id, ...props }, ref) => {
  const inputId = id ?? props.name;
  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={inputId}
        className="text-xs font-semibold uppercase tracking-wide text-graphite-500"
      >
        {label}
      </label>
      <input
        ref={ref}
        id={inputId}
        className={cn(
          "h-11 rounded-lg border border-graphite-300 bg-white px-3.5 text-[15px] text-graphite-900 placeholder:text-graphite-400 transition-colors",
          "hover:border-graphite-400 focus:border-ford-500",
          className,
        )}
        {...props}
      />
      {hint ? <span className="text-xs text-graphite-400">{hint}</span> : null}
    </div>
  );
});
Input.displayName = "Input";
