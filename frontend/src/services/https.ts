/**
 * Base HTTP service for handling API requests
 * Provides environment-aware URL construction and error handling
 */

/**
 * Determines the appropriate API base URL based on execution environment
 * @returns The base URL for API requests
 */
export const getApiBaseUrl = (): string => {
    // When running on the server (Node.js environment)
    if (typeof window === 'undefined') {
      return process.env.NEXT_PUBLIC_CONTAINER_API_URL || '';
    }
    // When running in the browser
    console.log(process.env.NEXT_PUBLIC_API_URL)
    return process.env.NEXT_PUBLIC_API_URL;
  };

  /**
   * Enhanced fetch function with error handling and type safety
   * @param endpoint - The API endpoint to call (without base URL)
   * @param options - Standard fetch options
   * @returns Promise with the parsed response data
   */
  export async function fetchApi<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const baseUrl = getApiBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return await response.json() as T;
    } catch (error) {
      console.error(`Error fetching from ${endpoint}:`, error);
      throw error;
    }
  }
