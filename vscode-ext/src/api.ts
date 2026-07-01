import * as https from 'https';

export interface UsageDay {
  date: string;
  total_tokens: number;
  cache_hit_tokens: number;
  cache_miss_tokens: number;
  model_usage: Record<string, number>;
  model_detail: Record<string, {
    tokens: number;
    cache_hit: number;
    cache_miss: number;
    requests: number;
  }>;
}

export interface BalanceInfo {
  total: number;
  granted: number;
  topped_up: number;
}

interface UsageAmount {
  prompt_tokens: number;
  cache_hit_tokens: number;
  cache_miss_tokens: number;
  response_tokens: number;
  requests: number;
}

const DEEPSEEK_USAGE_URL = 'https://platform.deepseek.com/api/v0/usage/amount';
const DEEPSEEK_BALANCE_URL = 'https://platform.deepseek.com/api/v0/user/balance';
const BROWSER_HEADERS: Record<string, string> = {
  'accept': '*/*',
  'accept-language': 'zh-CN,zh;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'referer': 'https://platform.deepseek.com/usage',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'x-client-bundle-id': 'com.deepseek.chat',
  'x-client-locale': 'zh_CN',
  'x-client-platform': 'web',
  'x-client-version': '1.0.0',
};

function httpGet(url: string, headers: Record<string, string>): Promise<string> {
  return new Promise((resolve, reject) => {
    https.get(url, { headers }, (res) => {
      let data = '';
      res.on('data', (chunk: string) => data += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
        } else {
          resolve(data);
        }
      });
    }).on('error', reject);
  });
}

function extractAmounts(usageList: any[] | undefined): UsageAmount {
  const result: UsageAmount = {
    prompt_tokens: 0,
    cache_hit_tokens: 0,
    cache_miss_tokens: 0,
    response_tokens: 0,
    requests: 0,
  };
  const typeMap: Record<string, keyof UsageAmount> = {
    PROMPT_TOKEN: 'prompt_tokens',
    PROMPT_CACHE_HIT_TOKEN: 'cache_hit_tokens',
    PROMPT_CACHE_MISS_TOKEN: 'cache_miss_tokens',
    RESPONSE_TOKEN: 'response_tokens',
    REQUEST: 'requests',
  };
  for (const item of usageList || []) {
    const key = typeMap[item.type];
    if (key) {
      result[key] += parseInt(String(item.amount), 10) || 0;
    }
  }
  return result;
}

export async function fetchUsageHistory(
  bearerToken: string,
  cfClearance: string
): Promise<UsageDay[]> {
  const now = new Date();
  const endDate = now.toISOString().slice(0, 10);
  const start = new Date(now);
  start.setDate(start.getDate() - 6);
  const startDate = start.toISOString().slice(0, 10);

  const headers: Record<string, string> = {
    ...BROWSER_HEADERS,
    authorization: `Bearer ${bearerToken}`,
    cookie: `cf_clearance=${cfClearance}`,
  };

  const url = `${DEEPSEEK_USAGE_URL}?month=${now.getMonth() + 1}&year=${now.getFullYear()}`;
  const raw = await httpGet(url, headers);
  const data = JSON.parse(raw);

  if (data.code !== 0) {
    throw new Error(`API error: ${data.msg || 'unknown'}`);
  }

  const daysData: any[] = data?.data?.biz_data?.days || [];
  const normDict: Record<string, UsageDay> = {};

  for (const day of daysData) {
    const dateStr = String(day.date || '').slice(0, 10);
    if (dateStr < startDate || dateStr > endDate) continue;

    let dayTotal = 0, dayCacheHit = 0, dayCacheMiss = 0;
    const modelDetail: Record<string, UsageDay['model_detail'][string]> = {};

    for (const entry of day.data || []) {
      const modelName = entry.model || 'unknown';
      const amts = extractAmounts(entry.usage);
      const total = amts.prompt_tokens + amts.cache_hit_tokens + amts.cache_miss_tokens + amts.response_tokens;
      modelDetail[modelName] = {
        tokens: total,
        cache_hit: amts.cache_hit_tokens,
        cache_miss: amts.cache_miss_tokens,
        requests: amts.requests,
      };
      dayTotal += total;
      dayCacheHit += amts.cache_hit_tokens;
      dayCacheMiss += amts.cache_miss_tokens;
    }

    const modelUsage: Record<string, number> = {};
    for (const [m, d] of Object.entries(modelDetail)) {
      modelUsage[m] = d.tokens;
    }

    normDict[dateStr] = {
      date: dateStr,
      total_tokens: dayTotal,
      cache_hit_tokens: dayCacheHit,
      cache_miss_tokens: dayCacheMiss,
      model_usage: modelUsage,
      model_detail: modelDetail,
    };
  }

  // Fill missing days with zeros
  const result: UsageDay[] = [];
  const cursor = new Date(start);
  const end = new Date(endDate);
  while (cursor <= end) {
    const ds = cursor.toISOString().slice(0, 10);
    result.push(normDict[ds] || {
      date: ds, total_tokens: 0,
      cache_hit_tokens: 0, cache_miss_tokens: 0,
      model_usage: {}, model_detail: {},
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return result;
}

export async function getBalance(
  bearerToken: string,
  apiKey?: string
): Promise<BalanceInfo | null> {
  // Try API Key first (most reliable)
  if (apiKey) {
    try {
      const raw = await httpGet('https://api.deepseek.com/user/balance', {
        authorization: `Bearer ${apiKey}`,
        'content-type': 'application/json',
      });
      const data = JSON.parse(raw);
      if (data.is_available && data.balance_infos?.length) {
        const info = data.balance_infos[0];
        return {
          total: parseFloat(info.total_balance || '0'),
          granted: parseFloat(info.granted_balance || '0'),
          topped_up: parseFloat(info.topped_up_balance || '0'),
        };
      }
    } catch {
      // Fall through to platform API
    }
  }

  // Fallback: platform API with Bearer Token
  try {
    const url = 'https://platform.deepseek.com/api/v0/user/balance';
    const raw = await httpGet(url, {
      ...BROWSER_HEADERS,
      authorization: `Bearer ${bearerToken}`,
    });
    const data = JSON.parse(raw);
    if (data.is_available && data.balance_infos?.length) {
      const info = data.balance_infos[0];
      return {
        total: parseFloat(info.total_balance || '0'),
        granted: parseFloat(info.granted_balance || '0'),
        topped_up: parseFloat(info.topped_up_balance || '0'),
      };
    }
  } catch {
    // Give up
  }

  return null;
}
