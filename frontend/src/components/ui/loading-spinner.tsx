import type { SVGProps } from "react";
import { cn } from "../../lib/utils";

type LoadingSpinnerSize = "sm" | "md" | "lg";

type LoadingSpinnerProps = SVGProps<SVGSVGElement> & {
  size?: LoadingSpinnerSize;
};

const sizeClasses: Record<LoadingSpinnerSize, string> = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-6 w-6",
};

export function LoadingSpinner({
  size = "md",
  className,
  ...props
}: LoadingSpinnerProps) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      className={cn("animate-spin text-current", sizeClasses[size], className)}
      {...props}
    >
      <circle
        className="opacity-20"
        cx="12"
        cy="12"
        r="9"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        className="opacity-90"
        d="M21 12a9 9 0 0 1-9 9"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
