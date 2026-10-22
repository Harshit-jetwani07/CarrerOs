import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none",
          variant === "primary" && "bg-ink text-white hover:bg-cobalt",
          variant === "secondary" && "bg-cobalt-light text-cobalt-dark hover:bg-cobalt hover:text-white",
          variant === "ghost" && "text-ink hover:bg-black/5",
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
