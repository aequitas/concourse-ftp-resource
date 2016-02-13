import json
import logging


class Resource:
    def run(self, command_name: str, json_data: str, command_argument: str):
        data = json.loads(json_data)

        logging.debug('command: %s', command_name)
        logging.debug('input: %s', data)
        logging.debug('args: %s', command_argument)

        cmd = getattr(self, 'cmd_' + command_name)

        with self.context(**data['source']) as self.ftp:
            if command_argument:
                output = cmd(command_argument, **data.get('params', {}), **data.get('version', {}))
            else:
                output = cmd(**data.get('params', {}), **data.get('version', {}))

        return json.dumps(output)

    def context(self):
        raise NotImplemented()

    def cmd_check(self, *args, **kwargs):
        raise NotImplemented()

    def cmd_in(self, *args, **kwargs):
        raise NotImplemented()

    def cmd_out(self, *args, **kwargs):
        raise NotImplemented()
