/**
 * Type declarations for JavaScript store modules
 */

declare module './stores/index.js' {
  export function initializeStores(): Promise<void>;
}

declare module '../stores/index.js' {
  export function initializeStores(): Promise<void>;
}

declare module './stores' {
  export function initializeStores(): Promise<void>;
}
