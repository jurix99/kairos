/**
 * API Client for Kairos Backend
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// ========================================
// Types & Interfaces
// ========================================

export interface User {
  id: number;
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

export interface ExtractedEvent {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority: string;
  category_name: string;
}

export interface ChatResponse {
  message: string;
  events: ExtractedEvent[];
  action: string;
}

// Orchestration Types
export type NeedType = 'punctual_task' | 'habit_skill' | 'complex_project' | 'decision_research' | 'social_event';
export type NeedComplexity = 'simple' | 'moderate' | 'complex' | 'very_complex';
export type AgentType = 'executive' | 'coach' | 'strategist' | 'planner' | 'resource' | 'research' | 'social';

export interface NeedClassificationRequest {
  user_input: string;
  context?: Record<string, any>;
}

export interface NeedClassificationResponse {
  need_type: NeedType;
  complexity: NeedComplexity;
  suggested_agents: AgentType[];
  confidence: number;
  reasoning: string;
  key_characteristics: string[];
}

export interface AgentTaskRequest {
  agent_type: AgentType;
  user_input: string;
  need_type: NeedType;
  context?: Record<string, any>;
}

export interface AgentTaskResponse {
  agent_type: AgentType;
  success: boolean;
  result: Record<string, any>;
  message: string;
  next_steps: string[];
  created_goals: number[];
  created_events: number[];
}

export interface OrchestratedPlanRequest {
  user_input: string;
  include_calendar_integration?: boolean;
  create_goals?: boolean;
  create_events?: boolean;
}

export interface OrchestratedPlanResponse {
  classification: NeedClassificationResponse;
  agent_responses: AgentTaskResponse[];
  integrated_plan: Record<string, any>;
  summary: string;
  created_goals: number[];
  created_events: number[];
}

export interface AgentInfo {
  type: string;
  name: string;
  description: string;
  use_cases: string[];
}

export interface NeedTypeInfo {
  type: string;
  name: string;
  description: string;
  characteristics: string[];
  examples: string[];
  agents: string[];
}

// ========================================
// API Client Class
// ========================================

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }
  private getAuthHeaders(): HeadersInit {
    if (typeof window === 'undefined') {
      return {
        'Content-Type': 'application/json',
      };
    }
    const user = localStorage.getItem('kairos_user');
    if (user) {
      try {
        // The backend expects the user data as a Bearer token
        return {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user}`,
        };
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
    return {
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // ========================================
  // Assistant API
  // ========================================

  async chatWithAssistant(data: {
    message: string;
    conversation_history: Array<{ role: string; content: string }>;
  }): Promise<ChatResponse> {
    return this.request<ChatResponse>('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createEventsFromAssistant(data: {
    events: ExtractedEvent[];
  }): Promise<{ message: string; created_events: number[] }> {
    return this.request('/assistant/create-events', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ========================================
  // Orchestration API
  // ========================================

  /**
   * Classify a user need (Level 1)
   * Identifies the type of need and suggests appropriate agents
   */
  async classifyNeed(request: NeedClassificationRequest): Promise<NeedClassificationResponse> {
    return this.request<NeedClassificationResponse>('/api/orchestration/classify', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Execute a specific agent task (Level 2)
   * Allows manual invocation of a particular agent
   */
  async executeAgentTask(request: AgentTaskRequest): Promise<AgentTaskResponse> {
    return this.request<AgentTaskResponse>('/api/orchestration/agent/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Create a complete orchestrated plan
   * Main endpoint that combines classification + agent execution + integration
   */
  async createOrchestratedPlan(request: OrchestratedPlanRequest): Promise<OrchestratedPlanResponse> {
    return this.request<OrchestratedPlanResponse>('/api/orchestration/plan', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * List all available agents with their descriptions
   */
  async listAvailableAgents(): Promise<AgentInfo[]> {
    return this.request<AgentInfo[]>('/api/orchestration/agents', {
      method: 'GET',
    });
  }

  /**
   * List all need types recognized by the system
   */
  async listNeedTypes(): Promise<NeedTypeInfo[]> {
    return this.request<NeedTypeInfo[]>('/api/orchestration/need-types', {
      method: 'GET',
    });
  }

  /**
   * Check orchestration system health
   */
  async checkOrchestrationHealth(): Promise<{
    status: string;
    database: string;
    openai: string;
    agents_available: number;
    need_types_supported: number;
  }> {
    return this.request('/api/orchestration/health', {
      method: 'GET',
    });
  }
  // ========================================
  // Goals API
  // ========================================

  async getGoals(params?: {
    status?: string;
    category?: string;
    priority?: string;
  }): Promise<Goal[]> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });
    }
    const query = queryParams.toString();
    return this.request<Goal[]>(`/goals${query ? `?${query}` : ''}`, {
      method: 'GET',
    });
  }

  async createGoal(goal: Omit<Goal, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'completed_at'>): Promise<Goal> {
    return this.request<Goal>('/goals', {
      method: 'POST',
      body: JSON.stringify(goal),
    });
  }

  async getGoalById(goalId: number): Promise<Goal> {
    return this.request<Goal>(`/goals/${goalId}`, {
      method: 'GET',
    });
  }

  async updateGoal(goalId: number, goal: Partial<Goal>): Promise<Goal> {
    return this.request<Goal>(`/goals/${goalId}`, {
      method: 'PUT',
      body: JSON.stringify(goal),
    });
  }

  async deleteGoal(goalId: number): Promise<void> {
    return this.request<void>(`/goals/${goalId}`, {
      method: 'DELETE',
    });
  }
  // ========================================
  // Events API
  // ========================================

  async getEvents(filters?: {
    start_date?: string;
    end_date?: string;
    category_id?: number;
    priority?: string;
    status?: string;
  }): Promise<Event[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    const query = params.toString();
    return this.request<Event[]>(`/events${query ? `?${query}` : ''}`, {
      method: 'GET',
    });
  }

  async createEvent(event: Omit<Event, 'id' | 'user_id' | 'category' | 'created_at' | 'updated_at'>): Promise<Event> {
    return this.request<Event>('/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  async updateEvent(eventId: number, event: Partial<Event>): Promise<Event> {
    return this.request<Event>(`/events/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify(event),
    });
  }

  async deleteEvent(eventId: number): Promise<void> {
    return this.request<void>(`/events/${eventId}`, {
      method: 'DELETE',
    });
  }
  // ========================================
  // Categories API
  // ========================================

  async getCategories(): Promise<Category[]> {
    return this.request<Category[]>('/categories', {
      method: 'GET',
    });
  }

  async createCategory(category: Omit<Category, 'id'>): Promise<Category> {
    return this.request<Category>('/categories', {
      method: 'POST',
      body: JSON.stringify(category),
    });
  }

  async updateCategory(id: number, category: Partial<Category>): Promise<Category> {
    return this.request<Category>(`/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(category),
    });
  }

  async deleteCategory(id: number): Promise<void> {
    return this.request<void>(`/categories/${id}`, {
      method: 'DELETE',
    });
  }

  // ========================================
  // Calendar Integrations API
  // ========================================

  async getIntegrations(): Promise<CalendarIntegration[]> {
    return this.request<CalendarIntegration[]>('/integrations', {
      method: 'GET',
    });
  }

  async createIntegration(integration: CalendarIntegrationCreate): Promise<CalendarIntegration> {
    return this.request<CalendarIntegration>('/integrations', {
      method: 'POST',
      body: JSON.stringify(integration),
    });
  }

  async updateIntegration(id: number, updates: Partial<CalendarIntegrationCreate>): Promise<CalendarIntegration> {
    return this.request<CalendarIntegration>(`/integrations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteIntegration(id: number): Promise<void> {
    return this.request<void>(`/integrations/${id}`, {
      method: 'DELETE',
    });
  }

  async syncIntegration(id: number): Promise<SyncResult> {
    return this.request<SyncResult>(`/integrations/${id}/sync`, {
      method: 'POST',
    });
  }

  // ========================================
  // Suggestions API
  // ========================================

  async getSuggestions(status?: string): Promise<any[]> {
    const query = status ? `?status=${status}` : '';
    return this.request(`/api/suggestions/${query}`, {
      method: 'GET',
    });
  }

  async generateSuggestions(): Promise<any[]> {
    return this.request('/api/suggestions/generate', {
      method: 'POST',
    });
  }

  async updateSuggestionStatus(
    suggestionId: number,
    status: string
  ): Promise<any> {
    return this.request(`/api/suggestions/${suggestionId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // ========================================
  // Authentication API
  // ========================================

  async githubLogin(code: string, state: string): Promise<User> {
    const response = await fetch(`${this.baseURL}/auth/github/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'GitHub authentication failed');
    }
    return response.json();
  }
}

// ========================================
// Export singleton instance
// ========================================

export const apiClient = new APIClient(API_BASE_URL);
