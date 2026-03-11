create extension if not exists pgcrypto;

-- =========================================
-- TABLES
-- =========================================

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
    is_enabled boolean not null default true,
    scan_cooldown_minutes integer not null default 10,
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
    is_available boolean not null default true,
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
    session_token text not null,
    vote_date date not null,
    created_at timestamptz not null default now(),
    constraint uq_vote_dish_session unique (restaurant_id, dish_id, session_token)
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

create table if not exists game_sessions (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid not null references tables(id) on delete cascade,
    session_token varchar(120) not null,
    game_type varchar(30) not null default 'spin_wheel',
    played_date date not null,
    reward_code varchar(60) unique,
    reward_label varchar(120) not null,
    reward_status varchar(20) not null default 'issued',
    redeemed_at timestamptz,
    created_at timestamptz not null default now(),
    constraint uq_game_session_daily unique (restaurant_id, session_token, game_type, played_date)
);

create table if not exists game_reward_rules (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    rule_date date not null,
    label varchar(120) not null,
    weight integer not null default 1,
    redeemable boolean not null default false,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    constraint uq_game_reward_rule_daily_label unique (restaurant_id, rule_date, label)
);

create table if not exists table_access_sessions (
    id uuid primary key default gen_random_uuid(),
    table_id uuid not null references tables(id) on delete cascade,
    session_token varchar(120) not null,
    last_access_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    constraint uq_table_access_session unique (table_id, session_token)
);

create table if not exists scoring_settings (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null unique references restaurants(id) on delete cascade,
    vote_points integer not null default 1,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists dish_score_overrides (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    dish_id uuid not null references dishes(id) on delete cascade,
    score_date date not null,
    bonus_points integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint uq_dish_score_override_daily unique (restaurant_id, dish_id, score_date)
);

-- =========================================
-- INDEXES
-- =========================================

create index if not exists idx_categories_restaurant_id on categories(restaurant_id);
create index if not exists idx_tables_restaurant_id on tables(restaurant_id);
create index if not exists idx_dishes_restaurant_id on dishes(restaurant_id);
create index if not exists idx_dishes_category_id on dishes(category_id);
create index if not exists idx_votes_restaurant_date on votes(restaurant_id, vote_date);
create index if not exists idx_votes_dish_id on votes(dish_id);
create index if not exists idx_feedback_restaurant_id on feedback(restaurant_id);
create index if not exists idx_feedback_created_at on feedback(created_at);
create index if not exists idx_game_sessions_restaurant_id on game_sessions(restaurant_id);
create index if not exists idx_game_sessions_session_token on game_sessions(session_token);
create index if not exists idx_game_reward_rules_restaurant_date on game_reward_rules(restaurant_id, rule_date);
create index if not exists idx_dish_score_overrides_restaurant_date on dish_score_overrides(restaurant_id, score_date);
create index if not exists idx_table_access_sessions_table_id on table_access_sessions(table_id);
create index if not exists idx_table_access_sessions_last_access_at on table_access_sessions(last_access_at);

-- =========================================
-- RLS FUNCTION
-- =========================================

create or replace function get_user_restaurant_id()
returns uuid
language sql
security definer
set search_path = public
as $$
    select restaurant_id
    from users
    where id = auth.uid()
$$;

-- =========================================
-- ENABLE RLS
-- =========================================

alter table restaurants enable row level security;
alter table categories enable row level security;
alter table tables enable row level security;
alter table dishes enable row level security;
alter table users enable row level security;
alter table votes enable row level security;
alter table feedback enable row level security;
alter table game_sessions enable row level security;
alter table game_reward_rules enable row level security;
alter table scoring_settings enable row level security;
alter table dish_score_overrides enable row level security;
alter table table_access_sessions enable row level security;

-- =========================================
-- ADMIN / DASHBOARD POLICIES
-- =========================================

create policy restaurant_access
on restaurants
for select
using (id = get_user_restaurant_id());

create policy categories_isolation
on categories
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy tables_isolation
on tables
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy dishes_isolation
on dishes
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy users_isolation
on users
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy votes_isolation
on votes
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy feedback_isolation
on feedback
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy game_sessions_isolation
on game_sessions
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy game_reward_rules_isolation
on game_reward_rules
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy scoring_settings_isolation
on scoring_settings
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy dish_score_overrides_isolation
on dish_score_overrides
for all
using (restaurant_id = get_user_restaurant_id())
with check (restaurant_id = get_user_restaurant_id());

create policy table_access_sessions_isolation
on table_access_sessions
for all
using (
    exists (
        select 1
        from tables t
        where t.id = table_access_sessions.table_id
          and t.restaurant_id = get_user_restaurant_id()
    )
)
with check (
    exists (
        select 1
        from tables t
        where t.id = table_access_sessions.table_id
          and t.restaurant_id = get_user_restaurant_id()
    )
);

-- =========================================
-- PUBLIC MENU ACCESS (QR CLIENT)
-- =========================================

create policy public_menu_categories
on categories
for select
using (true);

create policy public_menu_dishes
on dishes
for select
using (is_available = true);

create policy public_votes_insert
on votes
for insert
with check (true);

create policy public_feedback_insert
on feedback
for insert
with check (true);

create policy public_game_sessions_insert
on game_sessions
for insert
with check (true);

commit;