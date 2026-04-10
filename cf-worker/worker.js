/**
 * Sell-Thru AI Worker — Cloudflare Worker
 * Proxies requests from sellthru-simulator to Anthropic API
 *
 * Deploy: npx wrangler deploy
 * Set secret: npx wrangler secret put ANTHROPIC_API_KEY
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: CORS_HEADERS });
    }

    if (!env.ANTHROPIC_API_KEY) {
      return new Response(JSON.stringify({ error: 'API key not configured' }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
        status: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const { category, data2023, data2024, data2025, q1_2026, user_actuals, stats_prediction } = body;

    // Build context-aware prompt
    const systemPrompt = `You are an expert sales forecaster specializing in consumer electronics (air conditioners) in Saudi Arabia for Samsung.

Your task: Analyze 3 years of sell-through data and provide month-by-month predictions for 2026 (Apr–Dec only, since Q1 is already confirmed actual data).

Key market knowledge you have:
- Saudi Arabia AC market: peaks in May–Aug (summer), secondary peak around Ramadan
- 2026 Ramadan: Feb 28–Mar 29 (already past, so April+ has no Ramadan effect)
- Window AC has historically unusual spikes in certain months due to channel stocking behavior
- Split AC is the dominant category (85%+ of volume)
- Floor Standing AC serves commercial/luxury segment
- Fiscal year aligns with calendar year

CRITICAL: Respond ONLY with valid JSON matching this exact schema:
{
  "predictions": {
    "Apr": <integer>,
    "May": <integer>,
    "Jun": <integer>,
    "Jul": <integer>,
    "Aug": <integer>,
    "Sep": <integer>,
    "Oct": <integer>,
    "Nov": <integer>,
    "Dec": <integer>
  },
  "annual_total": <integer (Q1 actual + Apr-Dec prediction)>,
  "yoy_vs_2025": <float percentage e.g. 5.2 for +5.2%>,
  "confidence": "high" | "medium" | "low",
  "reasoning": "<2-3 sentences explaining key factors driving your prediction>",
  "key_risks": ["<risk1>", "<risk2>"],
  "key_opportunities": ["<opp1>", "<opp2>"]
}`;

    // Calculate Q1 2026 total for context
    const q1Total = Object.values(q1_2026 || {}).reduce((s, v) => s + (v || 0), 0);
    const q1_2025 = { Jan: data2025?.Jan || 0, Feb: data2025?.Feb || 0, Mar: data2025?.Mar || 0 };
    const q1_2025Total = Object.values(q1_2025).reduce((s, v) => s + v, 0);
    const q1Yoy = q1_2025Total > 0 ? ((q1Total - q1_2025Total) / q1_2025Total * 100).toFixed(1) : 'N/A';

    const fy2025 = Object.values(data2025 || {}).reduce((s, v) => s + (v || 0), 0);
    const fy2024 = Object.values(data2024 || {}).reduce((s, v) => s + (v || 0), 0);
    const fy2023 = Object.values(data2023 || {}).reduce((s, v) => s + (v || 0), 0);

    const userMessage = `Category: ${category}

=== Historical Annual Totals ===
2023: ${fy2023.toLocaleString()} units
2024: ${fy2024.toLocaleString()} units
2025: ${fy2025.toLocaleString()} units

=== Monthly Sell-Through Data ===
2023: ${JSON.stringify(data2023)}
2024: ${JSON.stringify(data2024)}
2025: ${JSON.stringify(data2025)}

=== 2026 Status ===
Q1 2026 Confirmed Actuals: ${JSON.stringify(q1_2026)}
Q1 2026 Total: ${q1Total.toLocaleString()} units
Q1 YoY vs Q1 2025: ${q1Yoy}%
${user_actuals && Object.keys(user_actuals).length > 0 ? `User-confirmed actuals beyond Q1: ${JSON.stringify(user_actuals)}` : ''}

=== Statistical Model Reference (Holt-Winters Ensemble) ===
Apr-Dec 2026 stats prediction: ${JSON.stringify(stats_prediction)}

Now provide your Claude AI prediction for Apr–Dec 2026 for ${category}.`;

    // Call Anthropic API
    let aiResponse;
    try {
      const apiResp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: 'claude-haiku-4-5-20251001',
          max_tokens: 1024,
          system: systemPrompt,
          messages: [{ role: 'user', content: userMessage }],
        }),
      });

      aiResponse = await apiResp.json();
    } catch (err) {
      return new Response(JSON.stringify({ error: 'API call failed', detail: err.message }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const content = aiResponse?.content?.[0]?.text || '';

    // Extract JSON from Claude's response
    let prediction;
    try {
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      prediction = JSON.parse(jsonMatch?.[0] || content);
    } catch {
      return new Response(JSON.stringify({ error: 'Parse error', raw: content.slice(0, 500) }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    // Add usage info
    prediction._usage = aiResponse?.usage || {};
    prediction._model = aiResponse?.model || 'claude-haiku-4-5-20251001';
    prediction._generated_at = new Date().toISOString();

    return new Response(JSON.stringify(prediction), {
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  },
};
