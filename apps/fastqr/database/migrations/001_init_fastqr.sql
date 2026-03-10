create extension if not exists pgcrypto;

create table if not exists restaurants (
    id uuid primary key default gen_random_uuid(),
    name varchar(120) not null,
    slug varchar(120) not null unique,
    timezone varchar(80) not null default 'UTC',
    created_at timestamptz not null default now()
);

create table if not exists categories (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    name varchar(120) not null,
    sort_order integer not null default 0
);

create table if not exists tables (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    code varchar(30) not null,
    qr_token varchar(100) not null unique,
    created_at timestamptz not null default now(),
    constraint uq_table_code_restaurant unique (restaurant_id, code)
);

create table if not exists dishes (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    category_id uuid not null references categories(id) on delete cascade,
    name varchar(150) not null,
    description text,
    price_cents integer not null check (price_cents >= 0),
    image_url varchar(255),
    is_active boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    email varchar(190) not null unique,
    password_hash varchar(255) not null,
    role varchar(20) not null default 'manager',
    created_at timestamptz not null default now()
);

create table if not exists votes (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid not null references tables(id) on delete cascade,
    dish_id uuid not null references dishes(id) on delete cascade,
    session_id text not null,
    vote_date date not null,
    created_at timestamptz not null default now(),
    constraint uq_vote_daily_dish_session unique (restaurant_id, dish_id, session_id, vote_date)
);

create table if not exists feedback (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid references tables(id) on delete set null,
    rating integer not null check (rating between 1 and 5),
    comment text,
    session_id varchar(120) not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_categories_restaurant_id on categories(restaurant_id);
create index if not exists idx_tables_restaurant_id on tables(restaurant_id);
create index if not exists idx_dishes_restaurant_id on dishes(restaurant_id);
create index if not exists idx_dishes_category_id on dishes(category_id);
create index if not exists idx_votes_restaurant_date on votes(restaurant_id, vote_date);
create index if not exists idx_votes_dish_id on votes(dish_id);
create index if not exists idx_feedback_restaurant_id on feedback(restaurant_id);
create index if not exists idx_feedback_created_at on feedback(created_at);

commit;
