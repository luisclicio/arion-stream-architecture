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
  MONGO_URI: z.string().url(),
  SERVICE_TYPE: z.string().default('actuator'),
  SERVICE_NAME: z.string(),
  STACK_ID: z.string(),
  CLOCK_URL: z.string().url().optional().default('http://clock:8000'),
});

export type Env = z.infer<typeof envSchema>;

export const env = envSchema.parse(process.env);
