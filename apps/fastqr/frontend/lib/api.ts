const API_BASE = '/api/v1'

export async function api(path: string, options?: RequestInit) {
  const token =
    typeof window === 'undefined'
      ? null
      : localStorage.getItem('fastqr_token')

  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? 'API error')
  }

  const text = await res.text()
  return text ? JSON.parse(text) : null
}

/* =========================
   TYPES
========================= */

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
  is_enabled: boolean
  scan_cooldown_minutes: number
}

export interface LoginResponse {
  access_token: string
  restaurant_id: string
}

/* =========================
   API
========================= */

export const fastqrApi = {
  /* ===== AUTH ===== */

  login: (email: string, password: string) =>
    api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    }) as Promise<LoginResponse>,

  /* ===== PUBLIC MENU ===== */

  getMenu: (qrToken: string, sessionToken?: string) =>
    api(
      `/public/${qrToken}/menu${
        sessionToken
          ? `?session_token=${encodeURIComponent(sessionToken)}`
          : ''
      }`,
    ) as Promise<PublicMenu>,

  voteDish: (qrToken: string, dishId: string, sessionToken: string) =>
    api(`/public/${qrToken}/votes`, {
      method: 'POST',
      body: JSON.stringify({
        dish_id: dishId,
        session_token: sessionToken,
      }),
    }),

  /* ===== DASHBOARD ===== */

  getOverview: (restaurantId: string) =>
    api(
      `/dashboard/restaurants/${restaurantId}/overview`,
    ) as Promise<Overview>,

  getCategories: (restaurantId: string) =>
    api(
      `/dashboard/restaurants/${restaurantId}/categories`,
    ) as Promise<Category[]>,

  getDishes: (restaurantId: string) =>
    api(
      `/dashboard/restaurants/${restaurantId}/dishes`,
    ) as Promise<Dish[]>,

  createDish: (
    restaurantId: string,
    payload: {
      category_id: string
      name: string
      description?: string
      price_cents: number
      image_url?: string
      is_available: boolean
    },
  ) =>
    api(`/dashboard/restaurants/${restaurantId}/dishes`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }) as Promise<Dish>,

  updateDish: (
    restaurantId: string,
    dishId: string,
    payload: Partial<{
      category_id: string
      name: string
      description: string
      price_cents: number
      image_url: string
      is_available: boolean
    }>,
  ) =>
    api(
      `/dashboard/restaurants/${restaurantId}/dishes/${dishId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    ) as Promise<Dish>,

  /* ===== TABLES ===== */

  getTables: (restaurantId: string) =>
    api(
      `/dashboard/restaurants/${restaurantId}/tables`,
    ) as Promise<Table[]>,

  createTable: (restaurantId: string, code: string) =>
    api(`/dashboard/restaurants/${restaurantId}/tables`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }) as Promise<Table>,

  spinWheel: (qrToken: string, sessionToken: string) =>
    api(`/public/${qrToken}/games/spin`, {
      method: 'POST',
      body: JSON.stringify({
        session_token: sessionToken,
      }),
    }) as Promise<{
      reward_label: string
      redeemable: boolean
      reward_code?: string
    }>,
}