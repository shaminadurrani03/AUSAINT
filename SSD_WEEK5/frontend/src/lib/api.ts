import { supabase } from '@/integrations/supabase/client';

const API_URL = 'http://localhost:5001';

export const api = {
  // Auth endpoints
  auth: {
    signUp: async (email: string, password: string, fullName: string) => {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: fullName },
          emailRedirectTo: `${window.location.origin}/auth`
        }
      });
      return { data, error };
    },

    signIn: async (email: string, password: string) => {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });
      return { data, error };
    },

    signOut: async () => {
      const { error } = await supabase.auth.signOut();
      return { error };
    }
  },

  // Intelligence endpoints
  intelligence: {
    getReports: async () => {
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch(`${API_URL}/api/reports`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`
        }
      });
      return response.json();
    },

    createReport: async (type: string, target: string) => {
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch(`${API_URL}/api/intelligence/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({ [type]: target })
      });
      return response.json();
    }
  }
}; 