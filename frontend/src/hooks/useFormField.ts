import * as React from "react";
import { type FieldPath, type FieldValues } from "react-hook-form";

type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  name: TName;
};

export const FormFieldContext = React.createContext<
  FormFieldContextValue | undefined
>(undefined);

type FormItemContextValue = {
  id: string;
};

export const FormItemContext = React.createContext<
  FormItemContextValue | undefined
>(undefined);

export const useFormField = () => {
  const fieldContext = React.useContext(FormFieldContext);
  const itemContext = React.useContext(FormItemContext);

  if (!fieldContext) {
    throw new Error("useFormField should be used within <FormField>");
  }

  return {
    ...fieldContext,
    formItemId: itemContext?.id,
    formDescriptionId: `${itemContext?.id}-description`,
    formMessageId: `${itemContext?.id}-message`,
  };
};

export type { FormFieldContextValue, FormItemContextValue };
