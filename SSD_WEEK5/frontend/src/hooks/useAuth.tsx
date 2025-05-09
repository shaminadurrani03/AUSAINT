import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';

// Define the auth context type
interface AuthContextType {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName: string) => Promise<void>;
  signOut: () => Promise<void>;
  configError: boolean;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [configError, setConfigError] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Set up the auth state listener
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, currentSession) => {
        console.log('Auth state changed:', event);
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setIsLoading(false);
      }
    );

    // Initial session check
    const initializeAuth = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        console.log('Initial session check:', data.session);
        setSession(data.session);
        setUser(data.session?.user ?? null);
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Sign in function
  const signIn = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      console.log('Attempting to sign in:', email);
      
      const { data, error } = await api.auth.signIn(email, password);
      
      if (error) {
        console.error('Login error:', error);
        toast({
          title: "Login failed",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      
      if (data?.user) {
        console.log('Login successful for user:', data.user.id);
        toast({
          title: "Login successful",
          description: "Welcome back to AUSAINT OSINT Suite",
        });
        navigate("/dashboard");
      }
    } catch (error: any) {
      console.error('Unexpected login error:', error);
      toast({
        title: "Login error",
        description: error?.message || "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Sign up function
  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      setIsLoading(true);
      console.log('Starting signup process for:', email);
      
      const { data, error } = await api.auth.signUp(email, password, fullName);
      
      if (error) {
        console.error('Signup error:', error);
        toast({
          title: "Signup failed",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      
      if (data?.user) {
        console.log('User created successfully:', data.user.id);
        
        if (data.session === null) {
          console.log('Email confirmation required');
          toast({
            title: "Account created",
            description: "Please check your email to confirm your account before logging in.",
          });
          return;
        }
        
        toast({
          title: "Account created",
          description: "Welcome to AUSAINT OSINT Suite",
        });
        
        navigate("/dashboard");
      }
    } catch (error: any) {
      console.error('Unexpected signup error:', error);
      toast({
        title: "Signup error",
        description: error?.message || "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Sign out function
  const signOut = async () => {
    try {
      setIsLoading(true);
      const { error } = await api.auth.signOut();
      
      if (error) {
        console.error('Signout error:', error);
        toast({
          title: "Signout failed",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      
      toast({
        title: "Signed out",
        description: "You have been successfully signed out.",
      });
      
      navigate("/auth");
    } catch (error: any) {
      console.error('Unexpected signout error:', error);
      toast({
        title: "Signout error",
        description: error?.message || "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      session,
      isLoading,
      isAuthenticated: !!session,
      signIn,
      signUp,
      signOut,
      configError
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
