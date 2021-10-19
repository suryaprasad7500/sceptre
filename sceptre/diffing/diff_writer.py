import json
from abc import abstractmethod
from datetime import datetime
from typing import TextIO, Generic, List

import cfn_flip
import yaml
from deepdiff import DeepDiff

from sceptre.diffing.stack_differ import StackConfiguration, StackDiff, DiffType

deepdiff_json_defaults = {
    datetime.date: lambda x: x.isoformat(),
    StackConfiguration: lambda x: dict(x._asdict())
}


class DiffWriter(Generic[DiffType]):
    """A component responsible for taking a StackDiff and writing it in a way that is useful and
    readable. This is an abstract base class, so the abstract methods need to be implemented to
    create a DiffWriter for a given DiffType.
    """
    STAR_BAR = '*' * 80
    LINE_BAR = '-' * 80

    def __init__(self, stack_diff: StackDiff, output_stream: TextIO, output_format: str):
        """Initializes the DiffWriter

        :param stack_diff: The diff this writer will be outputting
        :param output_stream: The stream this writer should output to; Generally, this will be
            stdout
        :param output_format: Output format specified for the base Sceptre cli command; This should
            be one of "yaml", "json", or "text"
        """
        self.stack_name = stack_diff.stack_name
        self.stack_diff = stack_diff

        self.template_diff = stack_diff.template_diff
        self.config_diff = stack_diff.config_diff
        self.is_deployed = stack_diff.is_deployed

        self.output_stream = output_stream
        self.output_format = output_format

    @property
    def has_difference(self) -> bool:
        return self.has_config_difference or self.has_template_difference

    def write(self):
        """Writes the diff to the output stream."""
        self._output(self.STAR_BAR)
        if not self.has_difference:
            self._output(f"No difference to deployed stack {self.stack_name}")
            return

        self._output(f"--> Difference detected for stack {self.stack_name}!")

        if not self.is_deployed:
            self._write_new_stack_details()
            return

        self._output(self.LINE_BAR)
        self._write_config_difference()
        self._output(self.LINE_BAR)
        self._write_template_difference()

    def _write_new_stack_details(self):
        stack_config_text = self._dump_stack_config(self.stack_diff.generated_config)
        self._output(
            'This stack is not deployed yet!',
            self.LINE_BAR,
            'New Config:',
            '',
            stack_config_text,
            self.LINE_BAR,
            'New Template:',
            '',
            self.stack_diff.generated_template
        )
        return

    def _output(self, *lines: str):
        lines_with_breaks = [f'{line}\n' for line in lines]
        self.output_stream.writelines(lines_with_breaks)

    def _dump_stack_config(self, stack_config: StackConfiguration) -> str:
        stack_config_dict = dict(stack_config._asdict())
        dumped = self._dump_dict(stack_config_dict)
        return dumped

    def _dump_dict(self, dict_to_dump: dict) -> str:
        if self.output_format == "json":
            # There's not really a viable way to dump a template as "text" -> YAML is very readable
            dumper = cfn_flip.dump_json
        else:
            dumper = cfn_flip.dump_yaml

        dumped = dumper(dict_to_dump)
        return dumped

    def _write_config_difference(self):
        if not self.has_config_difference:
            self._output("No stack config difference")
            return

        diff_text = self.dump_diff(self.config_diff)
        self._output(
            'Config difference:',
            '',
            diff_text
        )

    def _write_template_difference(self):
        if not self.has_template_difference:
            self._output('No template difference')
            return

        diff_text = self.dump_diff(self.template_diff)
        self._output(
            'Template difference:',
            '',
            diff_text
        )

    @abstractmethod
    def dump_diff(self, diff: DiffType) -> str:
        """"Implement this method to write the DiffType to string"""

    @property
    @abstractmethod
    def has_config_difference(self) -> bool:
        """Implement this to indicate whether or not there is a config difference"""

    @property
    @abstractmethod
    def has_template_difference(self) -> bool:
        """Implement this to indicate whether or not there is a template difference"""


class DeepDiffWriter(DiffWriter[DeepDiff]):
    """A DiffWriter for StackDiffs where the DiffType is a DeepDiff object."""

    @property
    def has_config_difference(self) -> bool:
        return len(self.config_diff) > 0

    @property
    def has_template_difference(self) -> bool:
        return len(self.template_diff) > 0

    def dump_diff(self, diff: DeepDiff) -> str:
        jsonified = diff.to_json(default_mapping=deepdiff_json_defaults, indent=4)
        if self.output_format == 'json':
            return jsonified

        # Yaml is more readable, but DeepDiff doesn't provide to_yaml method.
        loaded = json.loads(jsonified)
        return yaml.dump(loaded)


class DiffLibWriter(DiffWriter[List[str]]):
    """A DiffWriter for StackDiffs where the DiffType is a a list of strings."""

    @property
    def has_config_difference(self) -> bool:
        return len(self.config_diff) > 0

    @property
    def has_template_difference(self) -> bool:
        return len(self.template_diff) > 0

    def dump_diff(self, diff: List[str]) -> str:
        # Difflib doesn't care about the output format since it only outputs strings. We would have
        # accounted for the output format in the differ itself rather than here.
        return '\n'.join(diff)
