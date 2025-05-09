import { supabase } from '@/integrations/supabase/client';

const API_URL = 'http://localhost:5001';

export const api = {
  // Auth endpoints
  auth: {
    signUp: async (email: string, password: string, fullName: string) => {
      return await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });
    },

    signIn: async (email: string, password: string) => {
      return await supabase.auth.signInWithPassword({
        email,
        password,
      });
    },

    signOut: async () => {
      return await supabase.auth.signOut();
    },

    updatePassword: async (currentPassword: string, newPassword: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("No user found");

      // First verify the current password
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: user.email!,
        password: currentPassword,
      });
      if (signInError) throw new Error("Current password is incorrect");

      // Then update to the new password
      const { error: updateError } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (updateError) throw updateError;
    },

    toggle2FA: async (enable: boolean) => {
      // Implement 2FA toggle logic here
      // This would typically involve calling your backend API
      throw new Error("2FA not implemented yet");
    },
  },

  settings: {
    getApiKey: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("No user found");

      const { data, error } = await supabase
        .from("user_settings")
        .select("api_key")
        .eq("user_id", user.id)
        .single();

      if (error) {
        if (error.code === "PGRST116") {
          // If no settings exist, create them
          return await api.settings.generateApiKey();
        }
        throw error;
      }

      return { apiKey: data.api_key };
    },

    generateApiKey: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("No user found");

      const newApiKey = crypto.randomUUID();

      const { data, error } = await supabase
        .from("user_settings")
        .upsert({
          user_id: user.id,
          api_key: newApiKey,
        })
        .select()
        .single();

      if (error) throw error;
      return { apiKey: data.api_key };
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
  }
}; 