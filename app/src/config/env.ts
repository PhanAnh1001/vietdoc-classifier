// Environment variable validation for Next.js frontend

const requiredEnvVars = ["NEXT_PUBLIC_API_URL"] as const;

type RequiredEnvVar = (typeof requiredEnvVars)[number];

function getRequiredEnv(key: RequiredEnvVar): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

export const env = {
  apiUrl: () => getRequiredEnv("NEXT_PUBLIC_API_URL"),
} as const;
