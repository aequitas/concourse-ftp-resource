import json
import logging


class Resource:
    """Generic resource implementation."""

    def run(self, command_name: str, json_data: str, command_argument: str):
        """Parse input/arguments, perform requested command return output."""
        data = json.loads(json_data)

        logging.debug('command: %s', command_name)
        logging.debug('input: %s', data)
        logging.debug('args: %s', command_argument)

        with self.context(**data['source']) as self.ftp:
            if command_name == 'check':
                output = self.cmd_check(version=data.get('version', {}))
            elif command_name == 'in':
                output = self.cmd_in(command_argument, **data.get('version', {}))
            elif command_name == 'out':
                output = self.cmd_out(command_argument, **data.get('params', {}))

        return json.dumps(output)
