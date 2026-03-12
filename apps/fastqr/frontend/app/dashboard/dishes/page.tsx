'use client'

import { useEffect, useMemo, useState } from 'react'
import { fastqrApi, type Category, type Dish } from '@/lib/api'

interface DishFormState {
  name: string
  description: string
  price: string
  category_id: string
  image_url: string
  is_available: boolean
}

const emptyForm: DishFormState = {
  name: '',
  description: '',
  price: '',
  category_id: '',
  image_url: '',
  is_available: true,
}

export default function DashboardDishesPage() {
  const [restaurantId, setRestaurantId] = useState<string | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [dishes, setDishes] = useState<Dish[]>([])

  const [newCategoryName, setNewCategoryName] = useState('')
  const [form, setForm] = useState<DishFormState>(emptyForm)
  const [editingDishId, setEditingDishId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const rid = localStorage.getItem('fastqr_restaurant_id')
    setRestaurantId(rid)
    if (!rid) {
      setError('Configura restaurant_id en /dashboard')
      setLoading(false)
      return
    }

    Promise.all([fastqrApi.getCategories(rid), fastqrApi.getDishes(rid)])
      .then(([cats, dishList]) => {
        setCategories(cats)
        setDishes(dishList)
        if (cats.length > 0) {
          setForm((prev) => ({ ...prev, category_id: cats[0].id }))
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const dishesByCategory = useMemo(() => {
    const map = new Map<string, Dish[]>()
    categories.forEach((c) => map.set(c.id, []))
    dishes.forEach((d) => {
      if (!map.has(d.category_id)) map.set(d.category_id, [])
      map.get(d.category_id)!.push(d)
    })
    return map
  }, [categories, dishes])

  const refresh = async () => {
    if (!restaurantId) return
    const [cats, dishList] = await Promise.all([
      fastqrApi.getCategories(restaurantId),
      fastqrApi.getDishes(restaurantId),
    ])
    setCategories(cats)
    setDishes(dishList)
  }

  const resetForm = () => {
    setEditingDishId(null)
    setForm({
      ...emptyForm,
      category_id: categories[0]?.id ?? '',
    })
  }

  const handleSaveDish = async () => {
    if (!restaurantId || !form.name.trim() || !form.category_id || !form.price.trim()) return
    const priceNum = Number(form.price)
    if (!Number.isFinite(priceNum) || priceNum < 0) {
      setError('El precio no es válido')
      return
    }

    setSaving(true)
    setError(null)
    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || undefined,
      price_cents: Math.round(priceNum * 100),
      category_id: form.category_id,
      image_url: form.image_url.trim() || undefined,
      is_available: form.is_available,
    }

    try {
      if (editingDishId) {
        await fastqrApi.updateDish(restaurantId, editingDishId, payload)
      } else {
        await fastqrApi.createDish(restaurantId, payload)
      }
      await refresh()
      resetForm()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error guardando plato')
    } finally {
      setSaving(false)
    }
  }

  const toggleAvailability = async (dish: Dish) => {
    if (!restaurantId) return
    try {
      await fastqrApi.updateDish(restaurantId, dish.id, { is_available: !dish.is_available })
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar')
    }
  }

  return (
    <section className="stack-lg">
      {categories.map((category) => {
        const categoryDishes = dishesByCategory.get(category.id) ?? []

        return (
          <article key={category.id} className="card">
            <header style={{ marginBottom: 20, paddingBottom: 16, borderBottom: '1px solid var(--line)' }}>
              <h2 style={{ margin: 0, color: 'var(--text)' }}>
                {category.name}
              </h2>
            </header>

            {categoryDishes.length === 0 ? (
              <p className="muted" style={{ textAlign: 'center', padding: '20px 0', margin: 0 }}>
                No hay platos en esta categoría.
              </p>
            ) : (
              <div className="stack-lg">
                {categoryDishes.map((dish) => (
                  <div
                    key={dish.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      padding: '16px 0',
                      borderBottom: '1px solid var(--line-light)',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <p style={{ margin: 0, fontWeight: 600, fontSize: 15, color: 'var(--text)' }}>
                        {dish.name}
                      </p>

                      {dish.description && (
                        <p className="text-sm muted" style={{ margin: '4px 0 0 0' }}>
                          {dish.description}
                        </p>
                      )}

                      <p className="text-sm" style={{ margin: '8px 0 0 0', color: 'var(--primary)', fontWeight: 600 }}>
                        {(dish.price_cents / 100).toLocaleString('es-ES', {
                          style: 'currency',
                          currency: 'EUR',
                        })}
                      </p>
                    </div>

                    <div style={{ display: 'flex', gap: 12, marginLeft: 16, flexShrink: 0 }}>
                      <button
                        onClick={() => {
                          setEditingDishId(dish.id)

                          setForm({
                            name: dish.name,
                            description: dish.description ?? '',
                            price: (dish.price_cents / 100).toString(),
                            category_id: dish.category_id,
                            image_url: dish.image_url ?? '',
                            is_available: dish.is_available,
                          })
                        }}
                        className="btn btn-soft"
                      >
                        Editar
                      </button>

                      <button
                        onClick={() => toggleAvailability(dish)}
                        className={`btn ${
                          dish.is_available ? 'btn-danger' : 'btn-ok'
                        }`}
                      >
                        {dish.is_available ? 'Desactivar' : 'Activar'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </article>
        )
      })}
    </section>
  )
}
