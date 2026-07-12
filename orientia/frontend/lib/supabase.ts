import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Client-side Supabase instance — uses the anon key + RLS policies from
// backend/app/db/schema.sql, so it's safe to use directly in the browser
// for auth and for reads/writes scoped to the signed-in user.
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
