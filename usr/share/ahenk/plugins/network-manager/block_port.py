#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin

class BlockPort(AbstractPlugin):
    def __init__(self, task, context):
        super(BlockPort, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.ports = (self.task.get('ports') or "").strip()

        self.logger.debug('Parameters were initialized.')

    def add_rule(self, rule):
        try:
            self.execute(rule)
            self.logger.debug(f"Executed: {rule}")
        except Exception as e:
            self.logger.warning(f"Rule couldn't add: {rule} -> {e}")

    def handle_task(self):
        try:
            self.logger.debug('Writing to iptables ...')

            if not self.ports:
                raise ValueError("Ports parameter is empty.")

            for port in self.ports.split():
                if not port.isdigit():
                    self.logger.warning(f"Invalid port: '{port}', skipped.")
                    continue

                self.add_rule(f"iptables -A INPUT -p tcp --dport {port} -m state --state NEW,ESTABLISHED -j DROP")
                self.add_rule(f"iptables -A OUTPUT -p tcp --dport {port} -m state --state NEW,ESTABLISHED -j DROP")

            self.execute("iptables-save")
            self.logger.debug("iptables-save executed.")

            self.logger.info(f"NETWORK-MANAGER - Blocking Ports handled successfully: {self.ports}")
            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                message=f"Engellenen portlar: {self.ports}"
            )

        except Exception as e:
            self.logger.error(f"An error occurred while port blocking: {e}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message=f"NETWORK-MANAGER Block-Port hatası: {e}"
            )


def handle_task(task, context):
    domain = BlockPort(task, context)
    domain.handle_task()
