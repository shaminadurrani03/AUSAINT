import React, { useState } from 'react';
import { getSupabaseClient } from '../lib/supabase';

const SocialMediaIntelligence = () => {
  const [username, setUsername] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const supabase = getSupabaseClient();
      const { data, error } = await supabase.functions.invoke('search-username', {
        body: { username }
      });

      if (error) throw error;

      setResults(data);
    } catch (err) {
      console.error('Error searching username:', err);
      setError(err.message || 'Failed to search username');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Social Media Intelligence</h1>
      
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
            className="flex-1 p-2 border rounded"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {results && (
        <div className="bg-white shadow rounded p-4">
          <h2 className="text-xl font-semibold mb-2">Results for {username}</h2>
          <p className="mb-4">Found {results.found_count} profiles</p>
          
          <div className="space-y-2">
            {results.profiles.map((profile, index) => (
              <div key={index} className="flex items-center gap-2">
                <a
                  href={profile}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {profile}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialMediaIntelligence; 