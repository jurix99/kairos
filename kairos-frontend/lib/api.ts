// API client for Kairos backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface User {
  id: string;
  name: string;
  email: string;
  picture?: string;
  provider: string;
  external_id: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  color_code: string;
  user_id: number;
}

export interface Event {
  id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  is_flexible: boolean;
  category: Category;
  recurrence_rule?: string;
  user_id: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Get user from localStorage (browser only)
    if (typeof window !== 'undefined') {
      const savedUser = localStorage.getItem('kairos_user');
      if (savedUser) {
        try {
          const user = JSON.parse(savedUser);
          // Create auth token with external_id and provider
          const authToken = {
            id: user.external_id,  // Use external_id as id for auth
            provider: user.provider,
            name: user.name,
            email: user.email
          };
          headers['Authorization'] = `Bearer ${JSON.stringify(authToken)}`;
        } catch (error) {
          console.error('Error parsing saved user:', error);
        }
      }
    }

    return headers;
  }

  // Authentication
  async githubLogin(code: string, state: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/auth/github/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    });

    if (!response.ok) {
      throw new Error('GitHub login failed');
    }

    return response.json();
  }

  // Events
  async getEvents(): Promise<Event[]> {
    const response = await fetch(`${this.baseUrl}/events/`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch events');
    }

    return response.json();
  }

  async createEvent(event: Partial<Event>): Promise<Event> {
    const response = await fetch(`${this.baseUrl}/events/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      throw new Error('Failed to create event');
    }

    return response.json();
  }

  async updateEvent(id: number, event: Partial<Event>): Promise<Event> {
    const response = await fetch(`${this.baseUrl}/events/${id}/`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      throw new Error('Failed to update event');
    }

    return response.json();
  }

  async deleteEvent(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/events/${id}/`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete event');
    }
  }

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await fetch(`${this.baseUrl}/categories/`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }

    return response.json();
  }

  async createCategory(category: Partial<Category>): Promise<Category> {
    const response = await fetch(`${this.baseUrl}/categories/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(category),
    });

    if (!response.ok) {
      throw new Error('Failed to create category');
    }

    return response.json();
  }

  async deleteCategory(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/categories/${id}/`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete category');
    }
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
