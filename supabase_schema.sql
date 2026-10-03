-- Run this in your Supabase SQL Editor (Takes 5 seconds)
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Users table (tracks Telegram users and Notion connections)
create table if not exists users (
    id bigint primary key, -- Telegram Chat ID
    username text,
    first_name text,
    notion_api_key text,
    notion_database_id text,
    is_pro boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Tasks table
create table if not exists tasks (
    id uuid default uuid_generate_v4() primary key,
    user_id bigint references users(id) on delete cascade,
    title text not null,
    due_date text,
    priority text default 'medium',
    category text default 'Personal',
    completed boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Expenses table
create table if not exists expenses (
    id uuid default uuid_generate_v4() primary key,
    user_id bigint references users(id) on delete cascade,
    merchant text not null,
    amount numeric not null,
    currency text default 'USD',
    category text default 'General',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. Notes table
create table if not exists notes (
    id uuid default uuid_generate_v4() primary key,
    user_id bigint references users(id) on delete cascade,
    title text not null,
    summary text,
    tags text[],
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
