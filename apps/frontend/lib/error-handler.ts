/**
 * Error Handler Utility
 * Provides consistent error handling across the application
 */

import axios, { AxiosError } from 'axios'

export interface ErrorInfo {
  title: string
  message: string
  action?: string
  code?: string
}

export function handleApiError(error: unknown): ErrorInfo {
  // Axios error
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>
    
    // Network error (no response)
    if (!axiosError.response) {
      if (axiosError.code === 'ECONNABORTED') {
        return {
          title: 'Request Timeout',
          message: 'The request took too long to complete. Please try again.',
          action: 'Retry',
          code: 'TIMEOUT'
        }
      }
      
      return {
        title: 'Connection Error',
        message: 'Unable to connect to the server. Please check your internet connection and try again.',
        action: 'Retry',
        code: 'NETWORK_ERROR'
      }
    }
    
    // HTTP error responses
    const status = axiosError.response.status
    const data = axiosError.response.data
    
    switch (status) {
      case 400:
        return {
          title: 'Invalid Request',
          message: data?.error?.message || 'The request contains invalid data. Please check your input.',
          code: 'BAD_REQUEST'
        }
      
      case 401:
        return {
          title: 'Authentication Failed',
          message: data?.error?.message || 'Invalid email or password. Please try again.',
          code: 'UNAUTHORIZED'
        }
      
      case 403:
        return {
          title: 'Access Denied',
          message: data?.error?.message || "You don't have permission to perform this action.",
          code: 'FORBIDDEN'
        }
      
      case 404:
        return {
          title: 'Not Found',
          message: data?.error?.message || 'The requested resource was not found.',
          code: 'NOT_FOUND'
        }
      
      case 409:
        return {
          title: 'Conflict',
          message: data?.error?.message || 'This resource already exists or conflicts with existing data.',
          code: 'CONFLICT'
        }
      
      case 422:
        return {
          title: 'Validation Error',
          message: data?.error?.message || 'Please check your input and try again.',
          code: 'VALIDATION_ERROR'
        }
      
      case 429:
        return {
          title: 'Too Many Requests',
          message: 'You\'ve made too many requests. Please wait a moment and try again.',
          action: 'Wait',
          code: 'RATE_LIMIT'
        }
      
      case 500:
      case 502:
      case 503:
      case 504:
        return {
          title: 'Server Error',
          message: 'Something went wrong on our end. Our team has been notified. Please try again later.',
          action: 'Retry',
          code: 'SERVER_ERROR'
        }
      
      default:
        return {
          title: 'Error',
          message: data?.error?.message || 'An unexpected error occurred. Please try again.',
          code: 'UNKNOWN_ERROR'
        }
    }
  }
  
  // Generic error
  if (error instanceof Error) {
    return {
      title: 'Error',
      message: error.message || 'An unexpected error occurred',
      code: 'GENERIC_ERROR'
    }
  }
  
  // Unknown error
  return {
    title: 'Error',
    message: 'An unexpected error occurred',
    code: 'UNKNOWN'
  }
}

// Format validation errors from API
export function formatValidationErrors(errors: any[]): string {
  if (!Array.isArray(errors) || errors.length === 0) {
    return 'Please check your input'
  }
  
  return errors.map(err => {
    const field = err.loc?.join('.') || 'field'
    return `${field}: ${err.msg}`
  }).join(', ')
}
