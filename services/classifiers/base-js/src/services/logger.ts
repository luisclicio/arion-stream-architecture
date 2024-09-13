import { pino, stdTimeFunctions } from 'pino';

import { env } from '../env.js';

const transport = pino.transport({
  targets: [
    env.NODE_ENV === 'development'
      ? { target: 'pino-pretty' }
      : { target: 'pino/file' }, // STDOUT
  ],
});

export const logger = pino(
  {
    level: env.LOG_LEVEL,
    formatters: {
      level: (label) => {
        return { level: label.toUpperCase() };
      },
    },
    timestamp: stdTimeFunctions.isoTime,
  },
  transport,
);
