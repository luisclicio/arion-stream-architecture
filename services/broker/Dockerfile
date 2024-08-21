FROM rabbitmq:3.13-management-alpine
HEALTHCHECK --interval=30s --timeout=30s --start-period=20s --retries=5 CMD [ "rabbitmq-diagnostics", "-q", "ping" ]
EXPOSE 5672 15672
COPY ./rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
CMD [ "rabbitmq-server" ]
