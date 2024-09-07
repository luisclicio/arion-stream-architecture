FROM quay.io/minio/minio:latest
HEALTHCHECK --interval=5s --timeout=5s --start-period=5s --retries=5 \
  CMD [ "mc", "ready", "local" ]
EXPOSE 9000 9001
CMD [ "server", "/data", "--console-address", ":9001" ]
