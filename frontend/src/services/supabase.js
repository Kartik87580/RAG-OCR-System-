
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    console.error("Missing Supabase Keys. Checked VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.");
    throw new Error("Supabase URL and Key are required. Check your .env file and ensure it is accessible to Vite (envDir configuration).");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
