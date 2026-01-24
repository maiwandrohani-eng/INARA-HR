/**
 * Centralized API Configuration
 * Single source of truth for API base URL
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Get the full API URL for an endpoint
 * @param endpoint - The API endpoint (with or without leading slash)
 * @returns The full URL
 */
export function getApiUrl(endpoint: string): string {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_BASE_URL}/${cleanEndpoint}`
}
