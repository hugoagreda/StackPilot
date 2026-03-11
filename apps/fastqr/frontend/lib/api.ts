const API_BASE = '/api/v1'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('fastqr_token')
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken()
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body?.detail ?? res.statusText)
  }
  return res.json() as Promise<T>
}

// ─── Public types ────────────────────────────────────────────────────────────

export interface MenuDish {
  id: string
  name: string
  description?: string
  price_cents: number
}

export interface MenuCategory {
  id: string
  name: string
  dishes: MenuDish[]
}

export interface PublicMenu {
  restaurant: string
  table: string
  categories: MenuCategory[]
}

export interface RankingEntry {
  dish_id: string
  dish_name: string
  votes: number
  score: number
}

export interface TodayRanking {
  date: string
  ranking: RankingEntry[]
}

// ─── Auth types ───────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string
}

export interface MeResponse {
  user_id: string
  email: string
  role: string
  restaurant_id: string | null
}

// ─── Dashboard types ─────────────────────────────────────────────────────────

export interface Overview {
  total_votes: number
  unique_sessions: number
  avg_rating: number
  total_feedback: number
}

export interface Category {
  id: string
  name: string
}

export interface Dish {
  id: string
  restaurant_id: string
  category_id: string
  name: string
  description?: string
  price_cents: number
  image_url?: string
  is_available: boolean
}

export interface Table {
  id: string
  restaurant_id: string
  code: string
  qr_token: string
}

// ─── API ─────────────────────────────────────────────────────────────────────

export const api = {
  // Public
  getMenu: (qrToken: string, sessionToken: string) =>
    apiFetch<PublicMenu>(
      `/public/${qrToken}/menu?session_token=${encodeURIComponent(sessionToken)}`,
    ),

  vote: (qrToken: string, dishId: string, sessionToken: string) =>
    apiFetch<{ status: string }>(`/public/${qrToken}/votes`, {
      method: 'POST',
      body: JSON.stringify({ dish_id: dishId, session_token: sessionToken }),
    }),

  submitFeedback: (
    qrToken: string,
    rating: number,
    comment: string | undefined,
    sessionToken: string,
  ) =>
    apiFetch<{ status: string }>(`/public/${qrToken}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ rating, comment, session_token: sessionToken }),
    }),

  getRanking: (qrToken: string) =>
    apiFetch<TodayRanking>(`/public/${qrToken}/ranking/today`),

  // Auth
  login: (email: string, password: string) =>
    apiFetch<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => apiFetch<MeResponse>('/auth/me'),

  // Dashboard
  getOverview: (restaurantId: string) =>
    apiFetch<Overview>(`/dashboard/restaurants/${restaurantId}/overview`),

  getCategories: (restaurantId: string) =>
    apiFetch<Category[]>(`/dashboard/restaurants/${restaurantId}/categories`),

  createCategory: (restaurantId: string, name: string) =>
    apiFetch<Category>(`/dashboard/restaurants/${restaurantId}/categories`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),

  getDishes: (restaurantId: string) =>
    apiFetch<Dish[]>(`/dashboard/restaurants/${restaurantId}/dishes`),

  createDish: (
    restaurantId: string,
    data: {
      category_id: string
      name: string
      description?: string
      price_cents: number
      image_url?: string
      is_available: boolean
    },
  ) =>
    apiFetch<Dish>(`/dashboard/restaurants/${restaurantId}/dishes`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateDish: (
    restaurantId: string,
    dishId: string,
    data: Partial<{
      category_id: string
      name: string
      description: string
      price_cents: number
      image_url: string
      is_available: boolean
    }>,
  ) =>
    apiFetch<Dish>(`/dashboard/restaurants/${restaurantId}/dishes/${dishId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getTables: (restaurantId: string) =>
    apiFetch<Table[]>(`/dashboard/restaurants/${restaurantId}/tables`),

  createTable: (restaurantId: string, code: string) =>
    apiFetch<Table>(`/dashboard/restaurants/${restaurantId}/tables`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),
}
