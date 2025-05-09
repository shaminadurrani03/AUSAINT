import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useTheme } from "@/components/theme-provider";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { useLocation } from "react-router-dom";

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();
  const { toast } = useToast();
  const location = useLocation();
  const apiKeysRef = useRef<HTMLDivElement>(null);
  const [isDarkMode, setIsDarkMode] = useState(theme === "dark");
  const [isEmailNotifications, setIsEmailNotifications] = useState(false);
  const [reportFormat, setReportFormat] = useState("pdf");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);

  // Update isDarkMode when theme changes
  useEffect(() => {
    setIsDarkMode(theme === "dark");
  }, [theme]);

  // Handle hash navigation
  useEffect(() => {
    if (location.hash === "#api-keys" && apiKeysRef.current) {
      apiKeysRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [location.hash]);

  // Fetch API key on component mount
  useEffect(() => {
    const fetchApiKey = async () => {
      try {
        const response = await api.settings.getApiKey();
        setApiKey(response.apiKey);
      } catch (error) {
        console.error("Failed to fetch API key:", error);
        toast({
          title: "Error",
          description: "Failed to fetch API key",
          variant: "destructive",
        });
      }
    };
    fetchApiKey();
  }, [toast]);

  const handleDarkModeToggle = (checked: boolean) => {
    const newTheme = checked ? "dark" : "light";
    setTheme(newTheme);
    setIsDarkMode(checked);
    
    // Force immediate theme application
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(newTheme);
    
    toast({
      title: "Theme updated",
      description: `Switched to ${newTheme} mode`,
    });
  };

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      toast({
        title: "Error",
        description: "New passwords do not match",
        variant: "destructive",
      });
      return;
    }

    try {
      await api.auth.updatePassword(currentPassword, newPassword);
      toast({
        title: "Success",
        description: "Password changed successfully",
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to change password",
        variant: "destructive",
      });
    }
  };

  const handle2FAToggle = async () => {
    try {
      await api.auth.toggle2FA(!is2FAEnabled);
      setIs2FAEnabled(!is2FAEnabled);
      toast({
        title: "Success",
        description: `Two-factor authentication ${!is2FAEnabled ? "enabled" : "disabled"}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update 2FA settings",
        variant: "destructive",
      });
    }
  };

  const handleGenerateApiKey = async () => {
    try {
      const response = await api.settings.generateApiKey();
      setApiKey(response.apiKey);
      toast({
        title: "Success",
        description: "New API key generated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate API key",
        variant: "destructive",
      });
    }
  };

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText(apiKey);
    toast({
      title: "Success",
      description: "API key copied to clipboard",
    });
  };

  return (
    <div className="container py-10">
      <div className="grid gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
            <CardDescription>
              Manage your application preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive email notifications for new reports
                  </p>
                </div>
                <Switch
                  checked={isEmailNotifications}
                  onCheckedChange={setIsEmailNotifications}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Dark Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Toggle dark mode appearance
                  </p>
                </div>
                <Switch
                  checked={isDarkMode}
                  onCheckedChange={handleDarkModeToggle}
                />
              </div>
              <div className="space-y-2">
                <Label>Default Report Format</Label>
                <Select value={reportFormat} onValueChange={setReportFormat}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pdf">PDF</SelectItem>
                    <SelectItem value="csv">CSV</SelectItem>
                    <SelectItem value="json">JSON</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security</CardTitle>
            <CardDescription>
              Manage your security settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Change Password</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Change Password</DialogTitle>
                    <DialogDescription>
                      Enter your current password and choose a new one
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                      <Label htmlFor="current-password">Current Password</Label>
                      <Input
                        id="current-password"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="new-password">New Password</Label>
                      <Input
                        id="new-password"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="confirm-password">Confirm New Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={handlePasswordChange}>Save Changes</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Two-Factor Authentication</Label>
                  <p className="text-sm text-muted-foreground">
                    Add an extra layer of security to your account
                  </p>
                </div>
                <Switch
                  checked={is2FAEnabled}
                  onCheckedChange={handle2FAToggle}
                />
              </div>

              <div ref={apiKeysRef} id="api-keys" className="space-y-4">
                <div className="space-y-2">
                  <Label>API Key</Label>
                  <p className="text-sm text-muted-foreground">
                    Your API key for accessing the AUSAINT API
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    type={showApiKey ? "text" : "password"}
                    value={apiKey}
                    readOnly
                    className="font-mono"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? "Hide" : "Show"}
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleCopyApiKey}
                  >
                    Copy
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleGenerateApiKey}
                  >
                    Generate New
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 