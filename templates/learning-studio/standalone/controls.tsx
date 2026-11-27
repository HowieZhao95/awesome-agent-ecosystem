"use client";

import { Check, ChevronDown } from "lucide-react";
import { Checkbox, DropdownMenu, RadioGroup, Select } from "radix-ui";
import type { ComponentProps } from "react";
import { cn } from "../src/class-names";
import type { ChapterSelectProps, TemplateHost } from "../src/host";

function ExampleSelect({
  id,
  label,
  value,
  options,
  placeholder,
  onValueChange,
  lang,
}: ChapterSelectProps) {
  return (
    <Select.Root onValueChange={onValueChange} value={value}>
      <Select.Trigger aria-label={label} className="learning-select" id={id}>
        <Select.Value lang={lang} placeholder={placeholder} />
        <Select.Icon>
          <ChevronDown size={16} />
        </Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content
          className="learning-menu"
          collisionPadding={8}
          position="popper"
          sideOffset={4}
        >
          <Select.Viewport>
            {options.map((option) => (
              <Select.Item
                className="learning-option"
                key={option.value}
                value={option.value}
              >
                <Select.ItemText lang={lang}>{option.label}</Select.ItemText>
                <Select.ItemIndicator>
                  <Check size={15} />
                </Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}

const controls: Omit<TemplateHost, "t"> = {
  Button: ({ className, size, variant = "default", ...props }) => (
    <button
      {...props}
      className={cn("learning-button", className)}
      data-size={size}
      data-variant={variant}
    />
  ),
  Checkbox: ({ className, ...props }) => (
    <Checkbox.Root {...props} className={cn("learning-checkbox", className)}>
      <Checkbox.Indicator>
        <Check size={13} />
      </Checkbox.Indicator>
    </Checkbox.Root>
  ),
  RadioGroup: (props) => (
    <RadioGroup.Root {...props} className={cn("grid", props.className)} />
  ),
  RadioGroupItem: (props) => (
    <RadioGroup.Item
      {...props}
      className={cn("learning-radio", props.className)}
    >
      <RadioGroup.Indicator className="learning-radio-dot" />
    </RadioGroup.Item>
  ),
  DropdownMenu: DropdownMenu.Root,
  DropdownMenuTrigger: DropdownMenu.Trigger,
  DropdownMenuContent: (props) => (
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        {...props}
        className={cn("learning-menu", props.className)}
        sideOffset={4}
      />
    </DropdownMenu.Portal>
  ),
  DropdownMenuItem: (props) => (
    <DropdownMenu.Item
      {...props}
      className={cn("learning-option", props.className)}
    />
  ),
  Input: (props: ComponentProps<"input">) => (
    <input {...props} className={cn("learning-field", props.className)} />
  ),
  Textarea: (props: ComponentProps<"textarea">) => (
    <textarea {...props} className={cn("learning-field", props.className)} />
  ),
  Label: ({ htmlFor, children, ...props }) => (
    <label {...props} htmlFor={htmlFor}>
      {children}
    </label>
  ),
  LearningSelect: ExampleSelect,
  StudyImage: ({ image, resolveAsset, className }) => (
    // biome-ignore lint/performance/noImgElement: Standalone HTML has no framework image loader.
    <img
      alt={image.alt}
      className={cn("max-h-52 max-w-full rounded-lg object-contain", className)}
      height={200}
      src={resolveAsset(image.storagePath)}
      width={320}
    />
  ),
};

export default controls;
