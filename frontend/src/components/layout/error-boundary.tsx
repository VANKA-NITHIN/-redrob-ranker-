import React from "react"
import { Button } from "@/components/ui/button"
import { AlertTriangle, RefreshCw } from "lucide-react"

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex items-center justify-center h-[60vh] p-6">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 rounded-[16px] bg-danger/10 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-7 h-7 text-danger" />
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Something went wrong
            </h3>
            <p className="text-sm text-text-muted mb-6">
              An unexpected error occurred. Our team has been notified.
              Please try refreshing the page.
            </p>
            <Button
              variant="gradient"
              onClick={() => {
                this.setState({ hasError: false, error: null })
                window.location.reload()
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Page
            </Button>
            {this.state.error && (
              <details className="mt-4 text-left">
                <summary className="text-xs text-text-dim cursor-pointer hover:text-text-muted">
                  Technical details
                </summary>
                <pre className="mt-2 text-xs text-danger/80 bg-surface-secondary p-3 rounded-[8px] overflow-auto max-h-32">
                  {this.state.error.message}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
