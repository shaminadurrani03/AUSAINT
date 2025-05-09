import { useState } from "react";
import { Search, Share, User, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function SocialMediaIntelligence() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<null | {
    found: { name: string; url: string; category: string }[];
  }>(null);
  const [leakResults, setLeakResults] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.osint.searchUsername(username);
      if (response.success) {
        setResults({
          found: response.results
        });
      } else {
        setError(response.error || 'Failed to search username');
      }
    } catch (err) {
      setError('An error occurred while searching for the username');
      console.error('Error searching username:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLeakCheck = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLeakResults(null);

    try {
      const response = await fetch('http://localhost:3000/api/credential-leak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email })
      });

      if (!response.ok) {
        throw new Error('Failed to check credential leaks');
      }

      const data = await response.json();
      setLeakResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      social: "bg-blue-100 text-blue-800",
      tech: "bg-purple-100 text-purple-800",
      professional: "bg-green-100 text-green-800",
      forum: "bg-orange-100 text-orange-800",
      media: "bg-red-100 text-red-800",
      gaming: "bg-indigo-100 text-indigo-800",
      blog: "bg-yellow-100 text-yellow-800",
      other: "bg-gray-100 text-gray-800"
    };
    return colors[category as keyof typeof colors] || colors.other;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Social Media Intelligence</h1>
        <p className="text-muted-foreground mt-2">
          Find social media profiles and analyze digital footprint
        </p>
      </div>

      <Tabs defaultValue="username" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="username">Username Search</TabsTrigger>
          <TabsTrigger value="leaks">Credential Leaks</TabsTrigger>
        </TabsList>
        
        <TabsContent value="username" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Username Lookup</CardTitle>
              <CardDescription>
                Find user profiles across multiple platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="username">Username</Label>
                  <div className="flex gap-2">
                    <Input
                      id="username"
                      placeholder="Enter username to search"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                    <Button type="submit" disabled={loading}>
                      {loading ? "Searching..." : "Search"}
                    </Button>
                  </div>
                </div>
              </form>

              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
                  {error}
                </div>
              )}

              {results && (
                <div className="mt-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium">Found Profiles</h3>
                    <Badge variant="secondary">
                      {results.found.length} results
                    </Badge>
                  </div>
                  <Separator />
                  <div className="grid gap-4">
                    {results.found.map((profile) => (
                      <Card key={profile.name}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                                <User className="h-5 w-5" />
                              </div>
                              <div>
                                <h4 className="font-medium">{profile.name}</h4>
                                <p className="text-sm text-muted-foreground">
                                  {profile.url}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge className={getCategoryColor(profile.category)}>
                                {profile.category}
                              </Badge>
                              <Button variant="ghost" size="icon" asChild>
                                <a href={profile.url} target="_blank" rel="noopener noreferrer">
                                  <Share className="h-4 w-4" />
                                </a>
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="leaks">
          <Card>
            <CardHeader>
              <CardTitle>Credential Leak Check</CardTitle>
              <CardDescription>
                Search for leaked credentials in data breaches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLeakCheck} className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input 
                    id="email" 
                    placeholder="Enter email to check for breaches"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    type="email"
                    required
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Check Breaches
                    </>
                  )}
                </Button>
              </form>

              {error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {leakResults && (
                <div className="mt-4 space-y-4">
                  <Alert variant={leakResults.status === 'completed' ? 'default' : 'destructive'}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Report Status: {leakResults.status}</AlertTitle>
                    <AlertDescription>
                      {leakResults.status === 'completed' 
                        ? `Found ${leakResults.result?.email_leaks?.total_breaches || 0} breaches`
                        : 'Processing your request...'}
                    </AlertDescription>
                  </Alert>

                  {leakResults.status === 'completed' && leakResults.result?.email_leaks?.breaches && (
                    <div className="space-y-2">
                      <h4 className="font-medium">Found in Breaches:</h4>
                      <div className="grid gap-2">
                        {leakResults.result.email_leaks.breaches.map((breach, index) => (
                          <Card key={index}>
                            <CardHeader>
                              <CardTitle className="text-sm">{breach.title}</CardTitle>
                              <CardDescription>
                                {breach.description}
                              </CardDescription>
                            </CardHeader>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
