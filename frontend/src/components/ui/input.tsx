import * as React from "react";
import { cn } from "../../lib/utils";

const inputBaseStyles =
  "flex h-11 w-full rounded-xl border border-indigo-100 bg-white/90 px-4 py-2 text-sm text-indigo-950 shadow-sm shadow-indigo-950/5 backdrop-blur-md outline-none transition-all duration-200 placeholder:text-indigo-300 focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-500/15 disabled:cursor-not-allowed disabled:opacity-50";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(inputBaseStyles, className)}
        {...props}
      />
    );
  },
);

Input.displayName = "Input";

export { Input };
export type { InputProps };
