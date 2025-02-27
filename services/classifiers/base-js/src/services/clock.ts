import { env } from '../env.js';

type Source = 'system' | 'external';

export class Clock {
  static async now(source: Source = 'external'): Promise<Date> {
    if (source === 'system') {
      return new Date();
    }

    const response = await fetch(`${env.CLOCK_URL}/clock?response_type=text`);
    const text = await response.text();
    return new Date(text);
  }
}
