import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production']).default('development'),
  LOG_LEVEL: z
    .enum(['trace', 'debug', 'info', 'warn', 'error', 'fatal'])
    .transform((value) => value.toLowerCase())
    .default('info'),

  BROKER_HOST: z.string().default('localhost'),
  BROKER_PORT: z.coerce.number().default(5672),
  BROKER_USER: z.string().min(1),
  BROKER_PASSWORD: z.string().min(1),
});

export type Env = z.infer<typeof envSchema>;

export const env = envSchema.parse(process.env);
