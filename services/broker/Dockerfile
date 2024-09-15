FROM rabbitmq:3.13-management-alpine
HEALTHCHECK --interval=10s --timeout=10s --retries=5 \
  CMD [ "rabbitmq-diagnostics", "-q", "ping" ]
EXPOSE 5672 15672
COPY ./rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
CMD [ "rabbitmq-server" ]
