create extension if not exists pgcrypto;

-- =========================================
-- RESTAURANTS
-- =========================================

create table restaurants (
    id uuid primary key default gen_random_uuid(),
    name varchar(120) not null,
    slug varchar(120) not null unique,
    timezone varchar(80) not null default 'UTC',
    created_at timestamptz not null default now()
);

create table restaurant_settings (
    restaurant_id uuid primary key references restaurants(id) on delete cascade,
    primary_color varchar(20),
    secondary_color varchar(20),
    logo_url varchar(255),
    welcome_message text,
    currency varchar(10) default 'EUR',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- =========================================
-- USERS (DASHBOARD)
-- =========================================

create table users (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    email varchar(190) not null unique,
    password_hash varchar(255) not null,
    role varchar(20) not null default 'manager',
    created_at timestamptz not null default now()
);

create index idx_users_restaurant on users(restaurant_id);

-- =========================================
-- TABLES
-- =========================================

create table tables (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    code varchar(30) not null,
    qr_token varchar(60) not null unique,
    is_enabled boolean not null default true,
    scan_cooldown_minutes integer not null default 10,
    last_scan_at timestamptz,
    created_at timestamptz not null default now(),
    constraint uq_table_code_restaurant unique (restaurant_id, code)
);

create index idx_tables_restaurant on tables(restaurant_id);
create index idx_tables_qr_token on tables(qr_token);

-- =========================================
-- CATEGORIES
-- =========================================

create table categories (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    name varchar(120) not null,
    sort_order integer not null default 0,
    created_at timestamptz not null default now()
);

create index idx_categories_restaurant on categories(restaurant_id);

-- =========================================
-- DISHES
-- =========================================

create table dishes (
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

create index idx_dishes_restaurant on dishes(restaurant_id);
create index idx_dishes_category on dishes(category_id);
create index idx_dishes_available on dishes(restaurant_id, is_available);

-- =========================================
-- VOTES
-- =========================================

create table votes (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid not null references tables(id) on delete cascade,
    dish_id uuid not null references dishes(id) on delete cascade,
    session_token varchar(120) not null,
    vote_date date not null,
    created_at timestamptz not null default now(),
    constraint uq_vote unique (restaurant_id, table_id, dish_id, session_token)
);

create index idx_votes_restaurant on votes(restaurant_id);
create index idx_votes_dish on votes(dish_id);
create index idx_votes_table on votes(table_id);
create index idx_votes_date on votes(restaurant_id, vote_date);
create index idx_votes_ranking_daily on votes(restaurant_id, vote_date, dish_id);
create index idx_votes_session on votes(session_token);

-- =========================================
-- FEEDBACK
-- =========================================

create table feedback (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid references tables(id) on delete set null,
    rating integer not null check (rating between 1 and 5),
    comment text,
    session_token varchar(120) not null,
    created_at timestamptz not null default now()
);

create index idx_feedback_restaurant on feedback(restaurant_id);
create index idx_feedback_created on feedback(created_at);
create index idx_feedback_session on feedback(session_token);
create index idx_feedback_rating on feedback(restaurant_id, rating);

-- =========================================
-- TABLE ACCESS SESSIONS
-- =========================================

create table table_access_sessions (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid not null references tables(id) on delete cascade,
    session_token varchar(120) not null,
    created_at timestamptz not null default now(),
    last_access_at timestamptz not null default now(),
    constraint uq_table_access unique (table_id, session_token)
);

create index idx_sessions_restaurant on table_access_sessions(restaurant_id);
create index idx_sessions_table on table_access_sessions(table_id);
create index idx_sessions_session on table_access_sessions(session_token);

-- =========================================
-- GAME SESSIONS
-- =========================================

create table game_sessions (
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
    constraint uq_game_session unique (restaurant_id, session_token, game_type, played_date)
);

-- =========================================
-- GAME REWARD RULES
-- =========================================

create table game_reward_rules (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    rule_date date not null,
    label varchar(120) not null,
    weight integer not null default 1,
    redeemable boolean not null default false,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    constraint uq_game_rule unique (restaurant_id, rule_date, label)
);

-- =========================================
-- SCORING SETTINGS
-- =========================================

create table scoring_settings (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null unique references restaurants(id) on delete cascade,
    vote_points integer not null default 1,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- =========================================
-- DISH SCORE OVERRIDES
-- =========================================

create table dish_score_overrides (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    dish_id uuid not null references dishes(id) on delete cascade,
    score_date date not null,
    bonus_points integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint uq_dish_override unique (restaurant_id, dish_id, score_date)
);

-- =========================================
-- EVENTS (ANALYTICS)
-- =========================================

create table events (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid references tables(id),
    session_token varchar(120),
    event_type varchar(50) not null,
    event_data jsonb,
    created_at timestamptz not null default now()
);

create index idx_events_restaurant on events(restaurant_id);
create index idx_events_created on events(created_at);
create index idx_events_type on events(event_type);
create index idx_events_restaurant_created on events(restaurant_id, created_at);

-- =========================================
-- CAMPAIGNS
-- =========================================

create table campaigns (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    title varchar(120) not null,
    description text,
    campaign_type varchar(40),
    start_at timestamptz,
    end_at timestamptz,
    is_active boolean not null default true,
    created_at timestamptz not null default now()
);

create index idx_campaigns_restaurant on campaigns(restaurant_id);

-- =========================================
-- CAMPAIGN INTERACTIONS
-- =========================================

create table campaign_interactions (
    id uuid primary key default gen_random_uuid(),
    campaign_id uuid not null references campaigns(id) on delete cascade,
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    table_id uuid references tables(id),
    session_token varchar(120),
    interaction_type varchar(40) not null,
    created_at timestamptz not null default now()
);

create index idx_campaign_interactions_campaign on campaign_interactions(campaign_id);
create index idx_campaign_interactions_restaurant on campaign_interactions(restaurant_id);

-- =========================================
-- BILLING CUSTOMERS
-- =========================================

create table billing_customers (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null unique references restaurants(id) on delete cascade,
    stripe_customer_id varchar(120) not null unique,
    email varchar(190),
    created_at timestamptz not null default now()
);

-- =========================================
-- SUBSCRIPTIONS
-- =========================================

create table subscriptions (
    id uuid primary key default gen_random_uuid(),
    restaurant_id uuid not null references restaurants(id) on delete cascade,
    stripe_subscription_id varchar(120) not null unique,
    plan varchar(50) not null,
    status varchar(30) not null,
    current_period_start timestamptz,
    current_period_end timestamptz,
    cancel_at timestamptz,
    canceled_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index idx_subscriptions_restaurant on subscriptions(restaurant_id);
create index idx_subscriptions_status on subscriptions(status);