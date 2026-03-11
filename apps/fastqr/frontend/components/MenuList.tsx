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
      <section className="card">
        <p className="muted" style={{ margin: 0 }}>
          No hay platos disponibles en este momento.
        </p>
      </section>
    )
  }

  return (
    <div className="stack-lg">

      {categories.map((cat) => (
        <section key={cat.id}>

          <h2
            style={{
              marginBottom: 12,
              fontSize: 20,
              fontWeight: 700,
            }}
          >
            {cat.name}
          </h2>

          <div className="list">
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