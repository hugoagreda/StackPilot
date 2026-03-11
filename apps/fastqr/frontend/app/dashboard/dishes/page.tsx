'use client'

import { useEffect, useMemo, useState } from 'react'
import { api, type Category, type Dish } from '@/lib/api'

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
      setError('Restaurante no encontrado')
      setLoading(false)
      return
    }

    Promise.all([api.getCategories(rid), api.getDishes(rid)])
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
      api.getCategories(restaurantId),
      api.getDishes(restaurantId),
    ])
    setCategories(cats)
    setDishes(dishList)
  }

  const handleCreateCategory = async () => {
    if (!restaurantId || !newCategoryName.trim()) return
    try {
      await api.createCategory(restaurantId, newCategoryName.trim())
      setNewCategoryName('')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear categoría')
    }
  }

  const startEditDish = (dish: Dish) => {
    setEditingDishId(dish.id)
    setForm({
      name: dish.name,
      description: dish.description ?? '',
      price: (dish.price_cents / 100).toString(),
      category_id: dish.category_id,
      image_url: dish.image_url ?? '',
      is_available: dish.is_available,
    })
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
        await api.updateDish(restaurantId, editingDishId, payload)
      } else {
        await api.createDish(restaurantId, payload)
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
      await api.updateDish(restaurantId, dish.id, { is_available: !dish.is_available })
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar')
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Carta</h1>
        <p className="text-sm text-gray-500 mt-1">Gestiona tus platos por categoría.</p>
      </header>

      {error && <p className="text-sm text-red-500">{error}</p>}
      {loading && <p className="text-sm text-gray-400">Cargando...</p>}

      {!loading && (
        <>
          <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
            <h2 className="font-semibold mb-3">Nueva categoría</h2>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                placeholder="Ej: Entrantes"
                className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm"
              />
              <button
                onClick={handleCreateCategory}
                className="px-4 py-2 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-800"
              >
                Crear categoría
              </button>
            </div>
          </section>

          <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
            <h2 className="font-semibold mb-3">{editingDishId ? 'Editar plato' : 'Nuevo plato'}</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                placeholder="Nombre del plato"
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
              />

              <input
                value={form.price}
                onChange={(e) => setForm((p) => ({ ...p, price: e.target.value }))}
                type="number"
                min="0"
                step="0.01"
                placeholder="Precio"
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
              />

              <select
                value={form.category_id}
                onChange={(e) => setForm((p) => ({ ...p, category_id: e.target.value }))}
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>

              <input
                value={form.image_url}
                onChange={(e) => setForm((p) => ({ ...p, image_url: e.target.value }))}
                placeholder="URL imagen (opcional)"
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
              />

              <textarea
                value={form.description}
                onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                placeholder="Descripción"
                rows={3}
                className="md:col-span-2 rounded-lg border border-gray-200 px-3 py-2 text-sm resize-none"
              />

              <label className="md:col-span-2 flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={form.is_available}
                  onChange={(e) => setForm((p) => ({ ...p, is_available: e.target.checked }))}
                />
                Disponible para clientes
              </label>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={handleSaveDish}
                disabled={saving}
                className="px-4 py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600 disabled:opacity-50"
              >
                {saving ? 'Guardando...' : editingDishId ? 'Guardar cambios' : 'Crear plato'}
              </button>
              {editingDishId && (
                <button
                  onClick={resetForm}
                  className="px-4 py-2 rounded-lg border border-gray-200 text-sm"
                >
                  Cancelar
                </button>
              )}
            </div>
          </section>

          <section className="space-y-6">
            {categories.map((category) => {
              const categoryDishes = dishesByCategory.get(category.id) ?? []
              return (
                <div key={category.id} className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
                  <h3 className="font-semibold text-gray-900 mb-3">{category.name}</h3>
                  {categoryDishes.length === 0 ? (
                    <p className="text-sm text-gray-400">No hay platos en esta categoría.</p>
                  ) : (
                    <div className="space-y-2">
                      {categoryDishes.map((dish) => (
                        <div
                          key={dish.id}
                          className="flex items-center justify-between gap-3 rounded-xl border border-gray-100 p-3"
                        >
                          <div>
                            <p className="font-medium text-gray-900">{dish.name}</p>
                            <p className="text-sm text-gray-500">
                              {(dish.price_cents / 100).toLocaleString('es-ES', {
                                style: 'currency',
                                currency: 'EUR',
                              })}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => startEditDish(dish)}
                              className="px-3 py-1.5 rounded-lg text-sm border border-gray-200"
                            >
                              Editar
                            </button>
                            <button
                              onClick={() => toggleAvailability(dish)}
                              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                                dish.is_available
                                  ? 'bg-green-50 text-green-700 border border-green-200'
                                  : 'bg-gray-100 text-gray-500 border border-gray-200'
                              }`}
                            >
                              {dish.is_available ? 'Disponible' : 'No disponible'}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </section>
        </>
      )}
    </div>
  )
}
