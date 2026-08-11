// Jest setup for browser APIs used by animated/viewport-driven components.
// CRA loads this file automatically before tests.
class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | Document | null = null;
  readonly rootMargin: string = "0px";
  readonly scrollMargin: string = "0px";
  readonly thresholds: ReadonlyArray<number> = [];

  disconnect(): void {
    // no-op for test environment
  }

  observe(_target: Element): void {
    // no-op for test environment
  }

  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }

  unobserve(_target: Element): void {
    // no-op for test environment
  }
}

Object.defineProperty(globalThis, "IntersectionObserver", {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});
