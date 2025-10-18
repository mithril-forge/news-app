/**
 * API services for personal feed and custom prompts
 */
import { fetchApi } from '@/services/https';
import { NewsArticle } from '@/types';

/**
 * Account details interface matching backend
 */
export interface AccountDetails {
  id: number;
  email: string;
  prompt: string;
}

/**
 * Sets the custom AI prompt for a user
 * @param userEmail - User's email address
 * @param prompt - The custom prompt text
 */
export const setAIPrompt = async (userEmail: string, prompt: string): Promise<void> => {
  const params = new URLSearchParams();
  params.append('prompt', prompt);
  params.append('user_email', userEmail);

  return fetchApi<void>(`/ai_prompt/set?${params.toString()}`, {
    method: 'POST',
  });
};

/**
 * Gets account details for a user by email
 * @param userEmail - User's email address
 * @returns Account details or null if not found
 */
export const getAccountDetails = async (userEmail: string): Promise<AccountDetails | null> => {
  try {
    return await fetchApi<AccountDetails>(`/account_details/${encodeURIComponent(userEmail)}`);
  } catch (error) {
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
    throw error;
  }
};


/**
 * Response type for news pick containing articles and the original description
 */
export interface NewsPickResponse {
  articles: NewsArticle[];
  description: string;
}

/**
 * Gets all articles from the latest pick for a user along with the original prompt
 * @param userEmail - User's email address
 * @returns All news articles from the latest pick for the user and the original prompt
 */
export const getAllLatestPick = async (userEmail: string): Promise<NewsPickResponse> => {
  return fetchApi<NewsPickResponse>(`/get_latest_pick/${encodeURIComponent(userEmail)}`);
};

/**
 * Gets news articles for a specific pick hash along with the original prompt
 * @param pickHash - The hash of the pick
 * @returns Array of news articles for that pick and the original prompt
 */
export const getPickNews = async (pickHash: string): Promise<NewsPickResponse> => {
  return fetchApi<NewsPickResponse>(`/get_pick_news/${pickHash}`);
};

/**
 * Unified pick generation function that handles both anonymous and logged-in users
 * @param options - Generation options
 * @returns Pick response with hash for fetching articles
 */
export const generatePick = async (options: {
  userEmail?: string;
  prompt?: string;
}): Promise<PickGenerationResponse> => {
  const params = new URLSearchParams();

  if (options.userEmail) {
    params.append('user_email', options.userEmail);
  }

  if (options.prompt) {
    params.append('prompt', options.prompt);
  }

  return fetchApi<PickGenerationResponse>('/generate_pick', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });
};

/**
 * Pick generation response interface
 */
export interface PickGenerationResponse {
  message: string;
  hash: string; // The pick hash for referencing this pick later
}


/**
 * Links an anonymous pick (by hash) to a user account
 * @param userEmail - User's email address
 * @param pickHash - The hash of the anonymous pick to link
 */
export const linkAnonymousPickToUser = async (userEmail: string, pickHash: string): Promise<void> => {
  const params = new URLSearchParams();
  params.append('user_email', userEmail);
  params.append('pick_hash', pickHash);

  return fetchApi<void>('/link_anonymous_pick_to_user', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });
};


/**
 * Deletes a user account
 * @param userEmail - User's email address
 */
export const deleteAccount = async (userEmail: string): Promise<void> => {
  const params = new URLSearchParams();
  params.append('user_email', userEmail);

  return fetchApi<void>('/delete_account', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });
};