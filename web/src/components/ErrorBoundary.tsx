import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error?.message || 'Ocorreu um erro inesperado.',
    };
  }

  override componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Application ErrorBoundary:', error, info);
  }

  override render() {
    if (this.state.hasError) {
      return (
        <div style={{ maxWidth: 640, margin: '80px auto', padding: 24, fontFamily: 'Inter, system-ui, sans-serif' }}>
          <div className="notice">
            <h2>Algo correu mal</h2>
            <p>Não foi possível concluir a operação solicitada.</p>
            <button
              className="primaryBtn"
              onClick={() => this.setState({ hasError: false, message: '' })}
            >
              Tentar novamente
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
