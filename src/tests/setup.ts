// Test setup file for Jest
import 'jest-environment-jsdom';
import '@testing-library/jest-dom';

// Mock WebSocket for testing
const MockWebSocket = jest.fn().mockImplementation(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1,
}));

Object.assign(MockWebSocket, {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
});

(global as typeof globalThis & { WebSocket: typeof WebSocket }).WebSocket = MockWebSocket as unknown as typeof WebSocket;

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};
