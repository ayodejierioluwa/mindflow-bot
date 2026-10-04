-- Migration for Freemium limits and Telegram Stars payments
-- Run this in your Supabase SQL Editor

-- 1. Add usage_count and last_reset columns to users
alter table if exists users 
add column if not exists usage_count int default 0,
add column if not exists last_reset timestamp with time zone default timezone('utc'::text, now());

-- 2. Payments / Invoices table for Telegram Stars
create table if not exists payments (
    id uuid default gen_random_uuid() primary key,
    user_id bigint references users(id) on delete cascade,
    telegram_charge_id text,
    provider_payment_charge_id text,
    amount int, -- Telegram Stars (e.g. 250 stars)
    currency text default 'XTR', -- Telegram Stars Currency code
    status text default 'successful',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
