-- Schema Supabase/PostgreSQL para AGA HELP (multi-usuário + auditoria)
-- Execute no SQL Editor do projeto Supabase.

CREATE TABLE IF NOT EXISTS app_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    handle TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_history (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    user_handle TEXT NOT NULL,
    action_description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_history_order_id ON order_history (order_id);

ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_history ENABLE ROW LEVEL SECURITY;

-- Políticas permissivas para anon key (ajuste conforme sua estratégia de auth)
CREATE POLICY "app_users_anon_all" ON app_users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "order_history_anon_all" ON order_history FOR ALL USING (true) WITH CHECK (true);
