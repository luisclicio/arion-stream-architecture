export type ProcessorBaseData = {
  timestamp: string;
  deviceId: string;
  model: {
    name: string;
  };
  data: Record<string, unknown>;
};

export enum SeverityLevel {
  UNKNOWN = 0,
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
}
