import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from '../ErrorBoundary';

// Component that renders normally
function GoodChild() {
  return <div>正常渲染的子组件</div>;
}

// Component that throws an error
function BadChild() {
  throw new Error('测试错误：组件渲染失败');
}

describe('ErrorBoundary Component', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>
    );
    expect(screen.getByText('正常渲染的子组件')).toBeInTheDocument();
  });

  it('shows error UI when child throws', () => {
    // Suppress console.error for this test since we expect an error
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('渲染出错')).toBeInTheDocument();
    expect(screen.getByText('测试错误：组件渲染失败')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });

  it('retry button resets the error state', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Use a state-controlled component to toggle between good and bad
    let shouldThrow = true;
    
    function ToggleChild() {
      if (shouldThrow) {
        throw new Error('可重试的错误');
      }
      return <div>恢复成功</div>;
    }
    
    // Wrap in a component that forces re-render
    const { rerender } = render(
      <ErrorBoundary>
        <ToggleChild />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('渲染出错')).toBeInTheDocument();
    
    // Set up for successful render on retry
    shouldThrow = false;
    
    // Click retry button
    const retryButton = screen.getByText('重试');
    await user.click(retryButton);
    
    // After retry, the ErrorBoundary should reset and re-render children
    expect(screen.queryByText('渲染出错')).not.toBeInTheDocument();
    expect(screen.getByText('恢复成功')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
});
