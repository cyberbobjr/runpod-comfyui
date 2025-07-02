/**
 * Common Component Types
 * 
 * Type definitions for common/shared Vue components throughout the application.
 * These types are used across multiple components for consistency and type safety.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

/**
 * Size variants used across multiple components
 */
export type ComponentSize = 'xs' | 'm' | 'l'

/**
 * Button/component variants
 */
export type ComponentVariant = 
  | 'primary' 
  | 'secondary' 
  | 'danger' 
  | 'warning' 
  | 'success' 
  | 'info'
  | 'default'

/**
 * Alignment options
 */
export type ComponentAlign = 'left' | 'center' | 'right'

/**
 * Position options
 */
export type ComponentPosition = 'top' | 'bottom' | 'left' | 'right'

/**
 * Common component props that appear across multiple components
 */
export interface BaseComponentProps {
  /** Size variant of the component */
  size?: ComponentSize;
  /** Visual variant/style of the component */
  variant?: ComponentVariant;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Additional CSS classes to apply */
  className?: string;
  /** Title/tooltip text */
  title?: string;
}

/**
 * Icon-related props
 */
export interface IconProps {
  /** FontAwesome icon definition */
  icon?: any; // TODO: Improve typing when FontAwesome types are available
  /** Icon position relative to text */
  iconPosition?: 'left' | 'right';
}

/**
 * Modal/Dialog props
 */
export interface ModalProps {
  /** Whether the modal is visible */
  show: boolean;
  /** Maximum width of the modal */
  maxWidth?: string;
  /** Whether clicking outside closes the modal */
  closeOnOutsideClick?: boolean;
  /** Whether pressing escape closes the modal */
  closeOnEscape?: boolean;
}

/**
 * Dropdown/Menu props
 */
export interface DropdownProps extends BaseComponentProps {
  /** Button text for dropdown trigger */
  buttonText: string;
  /** Width of dropdown panel */
  dropdownWidth?: number;
  /** Alignment of dropdown relative to trigger */
  align?: ComponentAlign;
}

/**
 * Form component props
 */
export interface FormComponentProps extends BaseComponentProps {
  /** Input name attribute */
  name?: string;
  /** Input placeholder text */
  placeholder?: string;
  /** Whether the field is required */
  required?: boolean;
  /** Error message to display */
  error?: string;
  /** Help text to display */
  helpText?: string;
}

/**
 * Accordion component props
 */
export interface AccordionProps extends BaseComponentProps {
  /** Accordion title */
  title: string;
  /** Whether accordion is open by default */
  defaultOpen?: boolean;
}

/**
 * Card component props
 */
export interface CardProps {
  /** Card title */
  title?: string;
  /** Whether card has padding */
  padded?: boolean;
  /** Whether card has shadow */
  shadow?: boolean;
}

/**
 * Tooltip component props
 */
export interface TooltipProps {
  /** Tooltip text */
  text: string;
  /** Tooltip position */
  position?: ComponentPosition;
  /** Show delay in milliseconds */
  delay?: number;
}

/**
 * Empty state component props
 */
export interface EmptyStateProps {
  /** Title text */
  title?: string;
  /** Description text */
  description?: string;
  /** Icon to display */
  icon?: any;
  /** Whether to show action button */
  showAction?: boolean;
  /** Action button text */
  actionText?: string;
}

/**
 * Common component events
 */
export interface ComponentEvents {
  /** Click event */
  click: [event: MouseEvent];
  /** Input event */
  input: [value: any];
  /** Change event */
  change: [value: any];
  /** Focus event */
  focus: [event: FocusEvent];
  /** Blur event */
  blur: [event: FocusEvent];
}

/**
 * Utility type for component ref
 */
export type ComponentRef<T = HTMLElement> = T | null
