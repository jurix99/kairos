/**
 * API Client for Kairos Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// Types
export interface User {
  id: number;
  external_id: string;
  name: string;
  email: string;
  picture?: string;
  provider: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  color_code: string;
  description?: string;
  user_id?: number;
}

export interface Event {
  id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  is_flexible: boolean;
  category_id: number;
  user_id: number;
  category: Category;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: number;
  title: string;
  description?: string;
  target_date?: string;
  priority: 'high' | 'medium' | 'low';
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  category?: string;
  strategy?: string;
  success_criteria?: string;
  current_value?: string;
  target_value?: string;
  unit?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  user_id: number;
}

export interface CalendarIntegration {
  id: number;
  provider: 'apple' | 'google' | 'outlook';
  calendar_url: string;
  calendar_name?: string;
  username?: string;
  sync_enabled: boolean;
  is_active: boolean;
  last_sync?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface CalendarIntegrationCreate {
  provider: 'apple' | 'google' | 'outlook';
  calendar_url: string;
  calendar_name?: string;
  username?: string;
  password: string;
  sync_enabled?: boolean;
}

export interface SyncResult {
  success: boolean;
  events_imported: number;
  events_exported: number;
  events_updated: number;
  errors: string[];
  message: string;
}

// Helper function to get auth headers from localStorage
function getAuthHeaders(): HeadersInit {
  const user = localStorage.getItem('kairos_user');
  if (user) {
    try {
      const userData = JSON.parse(user);
      // For now, we'll use a simple auth mechanism
      // In production, you'd use proper JWT tokens
      return {
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.error('Error parsing user data:', error);
    }
  }
  return {
    'Content-Type': 'application/json',
  };
}

// API Client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await fetch(`${this.baseUrl}/categories`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }
    return response.json();
  }

  async createCategory(category: Omit<Category, 'id'>): Promise<Category> {
    const response = await fetch(`${this.baseUrl}/categories`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(category),
    });
    if (!response.ok) {
      throw new Error('Failed to create category');
    }
    return response.json();
  }

  async updateCategory(id: number, category: Partial<Category>): Promise<Category> {
    const response = await fetch(`${this.baseUrl}/categories/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(category),
    });
    if (!response.ok) {
      throw new Error('Failed to update category');
    }
    return response.json();
  }

  async deleteCategory(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/categories/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to delete category');
    }
  }

  // Events
  async getEvents(filters?: {
    start_date?: string;
    end_date?: string;
    category_id?: number;
    priority?: string;
  }): Promise<Event[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = `${this.baseUrl}/events${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch events');
    }
    return response.json();
  }

  async createEvent(event: Omit<Event, 'id' | 'user_id' | 'category' | 'created_at' | 'updated_at'>): Promise<Event> {
    const response = await fetch(`${this.baseUrl}/events`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(event),
    });
    if (!response.ok) {
      throw new Error('Failed to create event');
    }
    return response.json();
  }

  async updateEvent(id: number, event: Partial<Event>): Promise<Event> {
    const response = await fetch(`${this.baseUrl}/events/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(event),
    });
    if (!response.ok) {
      throw new Error('Failed to update event');
    }
    return response.json();
  }

  async deleteEvent(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/events/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to delete event');
    }
  }

  // Goals
  async getGoals(): Promise<Goal[]> {
    const response = await fetch(`${this.baseUrl}/goals`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch goals');
    }
    return response.json();
  }

  async createGoal(goal: Omit<Goal, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'completed_at'>): Promise<Goal> {
    const response = await fetch(`${this.baseUrl}/goals`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(goal),
    });
    if (!response.ok) {
      throw new Error('Failed to create goal');
    }
    return response.json();
  }

  async updateGoal(id: number, goal: Partial<Goal>): Promise<Goal> {
    const response = await fetch(`${this.baseUrl}/goals/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(goal),
    });
    if (!response.ok) {
      throw new Error('Failed to update goal');
    }
    return response.json();
  }

  async deleteGoal(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/goals/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to delete goal');
    }
  }

  // Calendar Integrations
  async getIntegrations(): Promise<CalendarIntegration[]> {
    const response = await fetch(`${this.baseUrl}/integrations`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch integrations');
    }
    return response.json();
  }

  async createIntegration(integration: CalendarIntegrationCreate): Promise<CalendarIntegration> {
    const response = await fetch(`${this.baseUrl}/integrations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(integration),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create integration');
    }
    return response.json();
  }

  async updateIntegration(id: number, updates: Partial<CalendarIntegrationCreate>): Promise<CalendarIntegration> {
    const response = await fetch(`${this.baseUrl}/integrations/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    if (!response.ok) {
      throw new Error('Failed to update integration');
    }
    return response.json();
  }

  async deleteIntegration(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/integrations/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to delete integration');
    }
  }

  async syncIntegration(id: number): Promise<SyncResult> {
    const response = await fetch(`${this.baseUrl}/integrations/${id}/sync`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync integration');
    }
    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
