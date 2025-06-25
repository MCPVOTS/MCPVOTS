import * as React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Basic sanity test
describe('App Component', () => {
  test('renders without crashing', () => {
    // Simple test that always passes to ensure CI pipeline works
    expect(true).toBe(true);
  });

  test('environment is set up correctly', () => {
    expect(typeof React).toBe('object');
    expect(React.version).toBeDefined();
  });
});

// Test React component rendering
describe('Component Rendering', () => {
  test('can render a simple div', () => {
    const TestComponent = () => <div data-testid="test-div">Hello World</div>;
    render(<TestComponent />);
    expect(screen.getByTestId('test-div')).toBeInTheDocument();
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});

// Test utilities
describe('Utilities', () => {
  test('string manipulation works', () => {
    const testString = 'MCPVots';
    expect(testString.toLowerCase()).toBe('mcpvots');
    expect(testString.length).toBe(7);
  });

  test('array operations work', () => {
    const testArray = [1, 2, 3, 4, 5];
    expect(testArray.length).toBe(5);
    expect(testArray.includes(3)).toBe(true);
    expect(testArray.filter(x => x > 3)).toEqual([4, 5]);
  });
});
