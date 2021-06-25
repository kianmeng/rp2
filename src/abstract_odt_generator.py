# Copyright 2021 eprbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from typing import Any, List, Set, Tuple

import ezodf

from abstract_generator import AbstractGenerator
from abstract_transaction import AbstractTransaction
from configuration import Configuration
from in_transaction import InTransaction
from out_transaction import OutTransaction
from rp2_error import RP2TypeError


class AbstractODTGenerator(AbstractGenerator):  # pylint: disable=W0223
    @staticmethod
    def _initialize_output_file(
        output_dir_path: str,
        output_file_prefix: str,
        output_file_name: str,
        template_sheets_to_keep: Set[str],
    ) -> Tuple[Any, str]:

        Configuration.type_check_string("output_dir_path", output_dir_path)
        Configuration.type_check_string("output_file_prefix", output_file_prefix)
        Configuration.type_check_string("output_file_name", output_file_name)
        if not isinstance(template_sheets_to_keep, Set):
            raise RP2TypeError(f"Parameter 'template_sheets_to_keep' is not a Set: {template_sheets_to_keep}")

        output_file_path: Path = Path(output_dir_path) / Path(f"{output_file_prefix}{output_file_name}")
        if Path(output_file_path).exists():
            output_file_path.unlink()

        template_path: str = str(Path(os.path.dirname(__file__)).parent.absolute() / Path("resources/template.ods"))
        output_file: Any = ezodf.newdoc("ods", str(output_file_path), template=template_path)

        index: int = 0
        sheet_name: str
        sheet_indexes_to_remove: List[int] = []
        for sheet_name in output_file.sheets.names():
            if sheet_name in template_sheets_to_keep:
                if not sheet_name.startswith("__"):
                    raise Exception(f"Internal error: template sheet '{sheet_name}' doesn't start with '__'")
                # Template sheets' names start with "__": remove leading "__" from name of sheet we want to keep
                output_file.sheets[index].name = sheet_name[2:]
            elif sheet_name.startswith("__"):
                # Template sheet we don't want to keep: mark it for removal
                sheet_indexes_to_remove.append(index)
            index += 1

        # Remove sheets that were marked for removal
        for index in reversed(sheet_indexes_to_remove):
            del output_file.sheets[index]

        return output_file, str(output_file_path)

    @staticmethod
    def _apply_style_to_cell(sheet: Any, row_index: int, column_index: int, style_name: str) -> None:
        Configuration.type_check_positive_int("row_index", row_index)
        Configuration.type_check_positive_int("column_index", column_index)
        Configuration.type_check_string("style_name", style_name)

        sheet[row_index, column_index].style_name = style_name

    def _fill_cell(
        self,
        sheet: Any,
        row_index: int,
        column_index: int,
        value: Any,
        visual_style: str = "transparent",
        data_style: str = "default",
    ) -> None:

        Configuration.type_check_string("visual_style", visual_style)
        Configuration.type_check_string("data_style", data_style)

        style_name = f"{visual_style}_{data_style}"
        sheet[row_index, column_index].set_value(value)
        self._apply_style_to_cell(sheet, row_index, column_index, style_name)

    def _fill_header(self, title: str, header: List[Tuple[str, str]], sheet: Any, row_index: int, column_index: int) -> int:

        Configuration.type_check_string("title", title)
        if not isinstance(header, List):
            raise RP2TypeError("Parameter 'header' is not a List")

        self._fill_cell(sheet, row_index, 0, title, visual_style="title")
        row_index += 1

        self._fill_cell(sheet, row_index, 0, "", visual_style="transparent")
        self._fill_cell(sheet, row_index + 1, 0, "", visual_style="transparent")

        header1: str
        header2: str
        i: int = 0
        for header1, header2 in header:
            self._fill_cell(sheet, row_index, column_index + i, header1, visual_style="header", data_style="default")
            self._fill_cell(sheet, row_index + 1, column_index + i, header2, visual_style="header", data_style="default")
            i += 1
        return row_index + 2

    @staticmethod
    def _get_table_type_from_transaction(transaction: AbstractTransaction) -> str:
        AbstractTransaction.type_check("transaction", transaction)
        if isinstance(transaction, InTransaction):
            return "IN"
        if isinstance(transaction, OutTransaction):
            return "OUT"
        return "INTRA"