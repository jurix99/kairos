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
  id: string;
  name: string;
  color: string; // Renommé de color_code à color pour consistance
  user_id: string;
}

export interface RecurrenceRule {
  type: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  daysOfWeek?: number[]; // 0 = Monday, 6 = Sunday
  endDate?: string;
  count?: number;
}

export interface Event {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  is_flexible: boolean;
  category_id: string; // Renommé de category à category_id pour consistance
  recurrence?: RecurrenceRule;
  user_id: string;
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

  async updateEvent(id: string, event: Partial<Event>): Promise<Event> {
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

  async deleteEvent(id: string): Promise<void> {
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

    const categories = await response.json();
    // Convert backend color_code to frontend color
    return categories.map((cat: any) => ({
      ...cat,
      color: cat.color_code || cat.color // Support both formats
    }));
  }

  async createCategory(category: Partial<Category>): Promise<Category> {
    // Convert frontend color to backend color_code
    const categoryData = {
      ...category,
      color_code: category.color,
      // Remove color field if it exists to avoid conflicts
      color: undefined
    };

    const response = await fetch(`${this.baseUrl}/categories/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(categoryData),
    });

    if (!response.ok) {
      throw new Error('Failed to create category');
    }

    const result = await response.json();
    return {
      ...result,
      color: result.color_code || result.color
    };
  }

  async deleteCategory(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/categories/${id}/`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete category');
    }
  }

  async updateCategory(id: string, category: Partial<Category>): Promise<Category> {
    // Convert frontend color to backend color_code
    const categoryData = {
      ...category,
      color_code: category.color,
      // Remove color field if it exists to avoid conflicts
      color: undefined
    };

    const response = await fetch(`${this.baseUrl}/categories/${id}/`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(categoryData),
    });

    if (!response.ok) {
      throw new Error('Failed to update category');
    }

    const result = await response.json();
    return {
      ...result,
      color: result.color_code || result.color
    };
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
