import { createClient } from '@supabase/supabase-js';
import { AuthResponse, AuthTokenResponsePassword } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

const API_URL = 'http://localhost:5001';

export const api = {
  // Auth endpoints
  auth: {
    signUp: async (email: string, password: string, fullName: string): Promise<AuthResponse> => {
      return supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });
    },

    signIn: async (email: string, password: string): Promise<AuthTokenResponsePassword> => {
      return supabase.auth.signInWithPassword({
        email,
        password,
      });
    },

    signOut: async () => {
      return supabase.auth.signOut();
    },

    updatePassword: async (currentPassword: string, newPassword: string) => {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      });
      if (error) throw error;
    },

    toggle2FA: async (enable: boolean) => {
      // TODO: Implement 2FA toggle
      throw new Error('2FA not implemented yet');
    },
  },

  settings: {
    getApiKey: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("No user found");

      try {
        const { data, error } = await supabase
          .from("user_settings")
          .select("api_key")
          .eq("user_id", user.id)
          .single();

        if (error) {
          console.error("Error fetching API key:", error);
          // If no settings exist, generate a new key
          if (error.code === "PGRST116") {
            return await api.settings.generateApiKey();
          }
          throw new Error("Failed to fetch API key. Please try again later.");
        }

        return { apiKey: data.api_key };
      } catch (error) {
        console.error("Error fetching API key:", error);
        throw new Error("Failed to fetch API key. Please try again later.");
      }
    },

    generateApiKey: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("No user found");

      try {
        // Generate a new API key
        const newApiKey = crypto.randomUUID();

        // First try to delete any existing settings
        const { error: deleteError } = await supabase
          .from("user_settings")
          .delete()
          .eq("user_id", user.id);

        if (deleteError) {
          console.error("Error deleting existing settings:", deleteError);
          // Continue anyway as the insert might still work
        }

        // Insert new settings
        const { data, error: insertError } = await supabase
          .from("user_settings")
          .insert({
            user_id: user.id,
            api_key: newApiKey,
          })
          .select()
          .single();

        if (insertError) {
          console.error("Error inserting new settings:", insertError);
          throw new Error("Failed to generate API key. Please try again later.");
        }

        return { apiKey: data.api_key };
      } catch (error) {
        console.error("Error generating API key:", error);
        throw new Error("Failed to generate API key. Please try again later.");
      }
    },
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
  },

  osint: {
    searchUsername: async (username: string) => {
      const { data, error } = await supabase.functions.invoke('search-username', {
        body: { username }
      });
      
      if (error) throw error;
      return data;
    }
  }
}; 