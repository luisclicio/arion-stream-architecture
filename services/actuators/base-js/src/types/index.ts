export type ProcessorBaseData = {
  timestamp: string;
  deviceId: string;
  model: {
    name: string;
  };
  data: Record<string, unknown>;
  severity: number;
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
    classifier: {
      service_name: string;
      received_data_timestamp: string;
      received_data_latency: number;
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
