-- Drop the trigger first
DROP TRIGGER IF EXISTS update_user_settings_updated_at ON user_settings;

-- Drop the function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop all policies
DROP POLICY IF EXISTS "Users can view their own settings" ON user_settings;
DROP POLICY IF EXISTS "Users can update their own settings" ON user_settings;
DROP POLICY IF EXISTS "Users can insert their own settings" ON user_settings;
DROP POLICY IF EXISTS "Users can delete their own settings" ON user_settings;

-- Drop the table
DROP TABLE IF EXISTS user_settings CASCADE; 