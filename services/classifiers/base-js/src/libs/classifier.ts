import { type ProcessorBaseData, SeverityLevel } from '../types/index.js';

export function getSeverityLevel(
  processorData: ProcessorBaseData,
): SeverityLevel {
  switch (processorData.model.name) {
    case 'people_detector': {
      const data = processorData.data as {
        peopleDetected: boolean;
        peopleCount: number;
        precision: number;
      };

      if (data.precision < 0.4) {
        return SeverityLevel.LOW;
      }

      if (data.peopleDetected && data.peopleCount > 2) {
        return SeverityLevel.HIGH;
      }

      if (data.peopleDetected && data.peopleCount > 0) {
        return SeverityLevel.MEDIUM;
      }

      return SeverityLevel.LOW;
    }

    default:
      return SeverityLevel.UNKNOWN;
  }
}
