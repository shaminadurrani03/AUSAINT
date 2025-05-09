import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { username } = await req.json()

    if (!username) {
      return new Response(
        JSON.stringify({ error: 'Username is required' }),
        { 
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Create a Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )

    // Search for username across platforms
    const platforms = [
      'github.com',
      'twitter.com',
      'instagram.com',
      'linkedin.com',
      'medium.com',
      'youtube.com',
      'reddit.com',
      'pinterest.com',
      'behance.net',
      'dribbble.com'
    ]

    const results = await Promise.all(
      platforms.map(async (platform) => {
        try {
          const response = await fetch(`https://${platform}/${username}`)
          return {
            platform,
            exists: response.status === 200,
            url: `https://${platform}/${username}`
          }
        } catch (error) {
          return {
            platform,
            exists: false,
            url: `https://${platform}/${username}`,
            error: error.message
          }
        }
      })
    )

    const foundProfiles = results.filter(result => result.exists)

    return new Response(
      JSON.stringify({
        username,
        found_count: foundProfiles.length,
        profiles: foundProfiles.map(p => p.url),
        success: true
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ 
        error: error.message,
        success: false 
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
}) 