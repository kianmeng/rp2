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

import unittest

from dateutil.tz import tzutc

from configuration import Configuration
from entry_types import TransactionType
from in_transaction import InTransaction
from intra_transaction import IntraTransaction
from rp2_error import RP2TypeError, RP2ValueError


class TestIntraTransaction(unittest.TestCase):
    _configuration: Configuration

    @classmethod
    def setUpClass(cls) -> None:
        TestIntraTransaction._configuration = Configuration("./config/test_data.config")

    def setUp(self) -> None:
        self.maxDiff = None

    def test_taxable_intra_transaction(self) -> None:
        intra_transaction: IntraTransaction = IntraTransaction(
            self._configuration,
            19,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BlockFi",
            "Alice",
            1000.0,
            2.0002,
            1.9998,
        )

        IntraTransaction.type_check("my_instance", intra_transaction)
        self.assertTrue(intra_transaction.is_taxable())
        self.assertEqual(0.4, intra_transaction.usd_taxable_amount)
        self.assertEqual(19, intra_transaction.line)
        self.assertEqual(2021, intra_transaction.timestamp.year)
        self.assertEqual(1, intra_transaction.timestamp.month)
        self.assertEqual(2, intra_transaction.timestamp.day)
        self.assertEqual(8, intra_transaction.timestamp.hour)
        self.assertEqual(42, intra_transaction.timestamp.minute)
        self.assertEqual(43, intra_transaction.timestamp.second)
        self.assertEqual(882000, intra_transaction.timestamp.microsecond)
        self.assertEqual(tzutc(), intra_transaction.timestamp.tzinfo)
        self.assertEqual("B1", intra_transaction.asset)
        self.assertEqual("Coinbase Pro", intra_transaction.from_exchange)
        self.assertEqual("Bob", intra_transaction.from_holder)
        self.assertEqual("BlockFi", intra_transaction.to_exchange)
        self.assertEqual("Alice", intra_transaction.to_holder)
        self.assertEqual(TransactionType.MOVE, intra_transaction.transaction_type)
        self.assertEqual(1000, intra_transaction.spot_price)
        self.assertEqual(2.0002, intra_transaction.crypto_sent)
        self.assertEqual(1.9998, intra_transaction.crypto_received)
        self.assertEqual(0.0004, intra_transaction.crypto_fee)
        self.assertEqual(0.4, intra_transaction.usd_fee)
        self.assertEqual(0.0004, intra_transaction.crypto_balance_change)
        self.assertEqual(0.4, intra_transaction.usd_balance_change)

        self.assertEqual(
            str(intra_transaction),
            """IntraTransaction:
  line=19
  timestamp=2021-01-02 08:42:43.882000 +0000
  asset=B1
  from_exchange=Coinbase Pro
  from_holder=Bob
  to_exchange=BlockFi
  to_holder=Alice
  transaction_type=TransactionType.MOVE
  spot_price=1000.0000
  crypto_sent=2.00020000
  crypto_received=1.99980000
  crypto_fee=0.00040000
  usd_fee=0.4000
  is_taxable=True
  usd_taxable_amount=0.4000""",
        )
        self.assertEqual(
            intra_transaction.to_string(2, repr_format=False, extra_data=["foobar", "qwerty"]),
            """    IntraTransaction:
      line=19
      timestamp=2021-01-02 08:42:43.882000 +0000
      asset=B1
      from_exchange=Coinbase Pro
      from_holder=Bob
      to_exchange=BlockFi
      to_holder=Alice
      transaction_type=TransactionType.MOVE
      spot_price=1000.0000
      crypto_sent=2.00020000
      crypto_received=1.99980000
      crypto_fee=0.00040000
      usd_fee=0.4000
      is_taxable=True
      usd_taxable_amount=0.4000
      foobar
      qwerty""",
        )
        self.assertEqual(
            intra_transaction.to_string(2, repr_format=True, extra_data=["foobar", "qwerty"]),
            (
                "    IntraTransaction("
                "line=19, "
                "timestamp='2021-01-02 08:42:43.882000 +0000', "
                "asset='B1', "
                "from_exchange='Coinbase Pro', "
                "from_holder='Bob', "
                "to_exchange='BlockFi', "
                "to_holder='Alice', "
                "transaction_type=<TransactionType.MOVE: 'move'>, "
                "spot_price=1000.0000, "
                "crypto_sent=2.00020000, "
                "crypto_received=1.99980000, "
                "crypto_fee=0.00040000, "
                "usd_fee=0.4000, "
                "is_taxable=True, "
                "usd_taxable_amount=0.4000, "
                "foobar, "
                "qwerty)"
            ),
        )

    def test_non_taxable_intra_transaction(self) -> None:
        intra_transaction: IntraTransaction = IntraTransaction(
            self._configuration,
            19,
            "2021-01-02T08:42:43.882Z",
            "B2",
            "Coinbase",
            "Bob",
            "Coinbase",
            "Alice",
            100.0,
            30,
            30,
        )
        self.assertFalse(intra_transaction.is_taxable())
        self.assertEqual(intra_transaction.usd_taxable_amount, 0)
        self.assertEqual("B2", intra_transaction.asset)
        self.assertEqual(TransactionType.MOVE, intra_transaction.transaction_type)
        self.assertEqual(0, intra_transaction.crypto_fee)
        self.assertEqual(0, intra_transaction.usd_fee)
        self.assertEqual(0, intra_transaction.crypto_balance_change)
        self.assertEqual(0.0, intra_transaction.usd_balance_change)

        self.assertEqual(
            str(intra_transaction),
            """IntraTransaction:
  line=19
  timestamp=2021-01-02 08:42:43.882000 +0000
  asset=B2
  from_exchange=Coinbase
  from_holder=Bob
  to_exchange=Coinbase
  to_holder=Alice
  transaction_type=TransactionType.MOVE
  spot_price=100.0000
  crypto_sent=30.00000000
  crypto_received=30.00000000
  crypto_fee=0.00000000
  usd_fee=0.0000
  is_taxable=False
  usd_taxable_amount=0.0000""",
        )

    def test_bad_to_string(self) -> None:
        intra_transaction: IntraTransaction = IntraTransaction(
            self._configuration,
            19,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BlockFi",
            "Alice",
            1000.0,
            2.0002,
            1.9998,
        )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'indent' has non-integer value"):
            intra_transaction.to_string(None, repr_format=False, extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'indent' has non-positive value.*"):
            intra_transaction.to_string(-1, repr_format=False, extra_data=["foobar", "qwerty"])
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'repr_format' has non-bool value .*"):
            intra_transaction.to_string(1, repr_format="False", extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'extra_data' is not of type List"):
            intra_transaction.to_string(1, repr_format=False, extra_data="foobar")  # type: ignore

    def test_bad_intra_transaction(self) -> None:
        with self.assertRaisesRegex(RP2TypeError, "Parameter name is not a string:.*"):
            IntraTransaction.type_check(None, None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type IntraTransaction:.*"):
            IntraTransaction.type_check("my_instance", None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type IntraTransaction: InTransaction"):
            IntraTransaction.type_check(
                "my_instance", InTransaction(self._configuration, 45, "2021-01-12T11:51:38Z", "B1", "BlockFi", "Bob", "BUY", 10000, 1, 0)
            )

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            IntraTransaction(
                None,  # type: ignore
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            IntraTransaction(
                "config",  # type: ignore
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'line' has non-positive value .*"):
            # Bad line
            IntraTransaction(
                self._configuration,
                -19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'line' has non-integer value .*"):
            # Bad line
            IntraTransaction(
                self._configuration,
                None,  # type: ignore
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'timestamp' has non-string value .*"):
            # Bad timestamp
            IntraTransaction(
                self._configuration,
                19,
                None,  # type: ignore
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'timestamp' value has no timezone info: .*"):
            # Bad timestamp
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'asset' value is not known: .*"):
            # Bad asset
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "hhh",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'asset' has non-string value .*"):
            # Bad asset
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                None,  # type: ignore
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'from_exchange' value is not known: .*"):
            # Bad from exchange
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "COinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'from_exchange' has non-string value .*"):
            # Bad from exchange
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                (1, 2, 3),  # type: ignore
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'from_holder' value is not known: .*"):
            # Bad from holder
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'from_holder' has non-string value .*"):
            # Bad from holder
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                None,  # type: ignore
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'to_exchange' value is not known: .*"):
            # Bad to exchange
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'to_exchange' has non-string value .*"):
            # Bad to exchange
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                None,  # type: ignore
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'to_holder' value is not known: .*"):
            # Bad to holder
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "A lice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'to_holder' has non-string value .*"):
            # Bad to holder
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                1111,  # type: ignore
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'spot_price' has non-positive value .*"):
            # Bad spot price
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                -1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'spot_price' has non-numeric value .*"):
            # Bad spot price
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                "1000",  # type: ignore
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_sent' has zero value"):
            # Bad crypto sent
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                0,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_sent' has non-positive value .*"):
            # Bad crypto sent
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                -2,
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_sent' has non-numeric value .*"):
            # Bad crypto sent
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                None,  # type: ignore
                1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_sent' has non-numeric value .*"):
            # Bad crypto sent
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                "-2.0002",  # type: ignore
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_received' has non-positive value .*"):
            # Bad crypto received
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                -2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_received' has non-numeric value .*"):
            # Bad crypto received
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                None,  # type: ignore
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_received' has non-numeric value .*"):
            # Bad crypto received
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                (1, 2, 3),  # type: ignore
            )

        with self.assertRaisesRegex(RP2ValueError, "IntraTransaction at line.*from/to exchanges/holders are the same: sending to self"):
            # From/to exchanges/holders are the same: sending to self
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "BlockFi",
                "Bob",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_sent' has non-positive value .*"):
            # Crypto sent < 0
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                -2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_sent' has zero value"):
            # Crypto sent == 0
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                0,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_received' has non-positive value .*"):
            # Crypto received < 0
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                -1.9998,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'notes' has non-string value .*"):
            # Bad notes
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
                notes=1111,  # type: ignore
            )
        with self.assertRaisesRegex(RP2ValueError, ".*IntraTransaction at line .*: from/to exchanges/holders are the same: sending to self"):
            # Sender and receiver are the same
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Alice",
                "BlockFi",
                "Alice",
                1000.0,
                2.0002,
                1.9998,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*IntraTransaction at line.*crypto sent < crypto received"):
            # Crypto sent < crypto received
            IntraTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "Coinbase Pro",
                "Bob",
                "BlockFi",
                "Alice",
                1000.0,
                1.0002,
                2.9998,
            )


if __name__ == "__main__":
    unittest.main()