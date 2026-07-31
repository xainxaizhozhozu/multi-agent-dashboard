import '@testing-library/jest-dom';

// Recharts ResponsiveContainer needs ResizeObserver
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};
