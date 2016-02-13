import json
import logging as log
import os
import tempfile


class Resource:
    """Generic resource implementation."""

    def run(self, command_name: str, json_data: str, command_argument: str):
        """Parse input/arguments, perform requested command return output."""
        data = json.loads(json_data)

        # allow debug logging to console for tests
        if os.environ.get('RESOURCE_DEBUG', False) or data.get('source', {}).get('debug', False):
            log.basicConfig(level=log.DEBUG)
        else:
            logfile = tempfile.NamedTemporaryFile(delete=False)
            log.basicConfig(level=log.DEBUG, filename=logfile)

        log.debug('command: %s', command_name)
        log.debug('input: %s', data)
        log.debug('args: %s', command_argument)

        with self.context(**data['source']) as self.ftp:
            if command_name == 'check':
                output = self.cmd_check(version=data.get('version', {}))
            elif command_name == 'in':
                output = self.cmd_in(command_argument, version=data.get('version'))
            elif command_name == 'out':
                output = self.cmd_out(command_argument, **data.get('params', {}))

        return json.dumps(output)
