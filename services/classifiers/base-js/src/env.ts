import { z } from 'zod';

export type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'fatal';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production']).default('development'),
  LOG_LEVEL: z
    .custom<LogLevel>((value) => {
      return ['trace', 'debug', 'info', 'warn', 'error', 'fatal'].includes(
        String(value).toLowerCase(),
      );
    }, 'Invalid log level')
    .default('info'),

  BROKER_RABBITMQ_CONNECTION_URI: z.string().url(),
  BROKER_RABBITMQ_EXCHANGE_NAME: z.string().default('arion'),
});

export type Env = z.infer<typeof envSchema>;

export const env = envSchema.parse(process.env);