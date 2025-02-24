export type ProcessorBaseData = {
  timestamp: string;
  deviceId: string;
  model: {
    name: string;
  };
  data: Record<string, unknown>;
  benchmark: {
    adapter: {
      service_name: string;
      image_id: number;
      sending_image_timestamp: string;
    };
    processor: {
      service_name: string;
      received_image_timestamp: string;
      received_image_latency: number;
      sending_data_timestamp: string;
    };
  };
};

export enum SeverityLevel {
  UNKNOWN = 0,
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
}
