with upsert_restaurant as (
    insert into restaurants (name, slug, timezone)
    values ('FastQR Demo Bistro', 'fastqr-demo-bistro', 'UTC')
    on conflict (slug) do update set name = excluded.name
    returning id
),
restaurant_ref as (
    select id from upsert_restaurant
    union all
    select id from restaurants where slug = 'fastqr-demo-bistro' limit 1
),
upsert_tables as (
    insert into tables (restaurant_id, code, qr_token)
    select id, 'T1', 'demo-token-t1' from restaurant_ref
    on conflict (qr_token) do nothing
    returning id
),
upsert_tables_2 as (
    insert into tables (restaurant_id, code, qr_token)
    select id, 'T2', 'demo-token-t2' from restaurant_ref
    on conflict (qr_token) do nothing
    returning id
),
upsert_categories as (
    insert into categories (restaurant_id, name, sort_order)
    select id, 'Starters', 1 from restaurant_ref
    union all
    select id, 'Main Dishes', 2 from restaurant_ref
    union all
    select id, 'Desserts', 3 from restaurant_ref
    returning id
)
select 1;

insert into dishes (restaurant_id, category_id, name, description, price_cents, is_active)
select r.id, c.id, 'Bruschetta', 'Toasted bread with tomato and basil', 690, true
from restaurants r
join categories c on c.restaurant_id = r.id and c.name = 'Starters'
where r.slug = 'fastqr-demo-bistro'
and not exists (
    select 1 from dishes d
    where d.restaurant_id = r.id and d.name = 'Bruschetta'
);

insert into dishes (restaurant_id, category_id, name, description, price_cents, is_active)
select r.id, c.id, 'Grilled Salmon', 'Salmon with seasonal vegetables', 1890, true
from restaurants r
join categories c on c.restaurant_id = r.id and c.name = 'Main Dishes'
where r.slug = 'fastqr-demo-bistro'
and not exists (
    select 1 from dishes d
    where d.restaurant_id = r.id and d.name = 'Grilled Salmon'
);

insert into dishes (restaurant_id, category_id, name, description, price_cents, is_active)
select r.id, c.id, 'Chocolate Mousse', 'Dark chocolate mousse with cream', 750, true
from restaurants r
join categories c on c.restaurant_id = r.id and c.name = 'Desserts'
where r.slug = 'fastqr-demo-bistro'
and not exists (
    select 1 from dishes d
    where d.restaurant_id = r.id and d.name = 'Chocolate Mousse'
);
