"use client";

import type { Checkbox, DropdownMenu, RadioGroup } from "radix-ui";
import {
  type ComponentProps,
  type ComponentType,
  createContext,
  useContext,
} from "react";
import type { ResolveAsset, TemplateImage } from "./types";

export type ChapterSelectProps = {
  id: string;
  label: string;
  value: string;
  options: readonly { value: string; label: string }[];
  placeholder?: string;
  lang?: string;
  onValueChange: (value: string) => void;
};

export type TemplateHost = {
  t: (key: string, params?: Record<string, string | number>) => string;
  Button: ComponentType<
    ComponentProps<"button"> & {
      size?: "sm" | "icon";
      variant?: "outline" | "ghost";
    }
  >;
  DropdownMenu: ComponentType<ComponentProps<typeof DropdownMenu.Root>>;
  DropdownMenuTrigger: ComponentType<
    ComponentProps<typeof DropdownMenu.Trigger>
  >;
  DropdownMenuContent: ComponentType<
    ComponentProps<typeof DropdownMenu.Content>
  >;
  DropdownMenuItem: ComponentType<ComponentProps<typeof DropdownMenu.Item>>;
  Checkbox: ComponentType<ComponentProps<typeof Checkbox.Root>>;
  RadioGroup: ComponentType<ComponentProps<typeof RadioGroup.Root>>;
  RadioGroupItem: ComponentType<ComponentProps<typeof RadioGroup.Item>>;
  Input: ComponentType<ComponentProps<"input">>;
  Label: ComponentType<ComponentProps<"label">>;
  Textarea: ComponentType<ComponentProps<"textarea">>;
  LearningSelect: ComponentType<ChapterSelectProps>;
  StudyImage: ComponentType<{
    image: TemplateImage;
    resolveAsset: ResolveAsset;
    className?: string;
  }>;
};
const Context = createContext<TemplateHost | null>(null);
export const LearningTemplateProvider = Context.Provider;
export function useTemplateHost() {
  const host = useContext(Context);
  if (!host) {
    throw new Error("LearningTemplateProvider is required");
  }
  return host;
}
