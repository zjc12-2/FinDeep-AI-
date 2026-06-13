"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: string;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-8 text-center">
            <p className="text-red-500 mb-2">页面发生错误</p>
            <p className="text-sm text-muted-foreground">{this.state.error}</p>
            <button
              onClick={() => this.setState({ hasError: false, error: "" })}
              className="mt-4 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm"
            >
              重试
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
