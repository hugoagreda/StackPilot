'use client'

import { DishCard } from './DishCard'
import type { MenuCategory } from '@/lib/api'

interface MenuListProps {
  categories: MenuCategory[]
  votedDishes: Set<string>
  onVote: (dishId: string) => void
}

export function MenuList({ categories, votedDishes, onVote }: MenuListProps) {
  if (categories.length === 0) {
    return (
      <p className="text-center text-gray-400 py-12">No hay platos disponibles en este momento.</p>
    )
  }

  return (
    <div className="space-y-8">
      {categories.map((cat) => (
        <section key={cat.id}>
          <h2 className="text-lg font-bold text-gray-800 mb-4 pb-2 border-b border-gray-100">
            {cat.name}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {cat.dishes.map((dish) => (
              <DishCard
                key={dish.id}
                {...dish}
                voted={votedDishes.has(dish.id)}
                onVote={onVote}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
