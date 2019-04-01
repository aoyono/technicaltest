import json

from rest_framework import status
from rest_framework.test import APISimpleTestCase, APITransactionTestCase

from bonds.models import Bond


class HelloWorld(APISimpleTestCase):
    def test_root(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class BondsAPI(APITransactionTestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.client.login(username='test', password='passwordtest')

    def test_bond_creation(self):
        bond = {
            "isin"    : "FR0000131104",
            "size"    : 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei"     : "R0MUWSFPU8MPRO8K5P83"
        }
        resp = self.client.post("/bonds/", data=bond, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp_content = json.loads(resp.content.decode('utf-8'))
        self.assertDictEqual(
            {
                k: v
                for k, v in resp_content.items()
                if k != 'url'
            },
            {
                "isin"      : "FR0000131104",
                "size"      : 100000000,
                "currency"  : "EUR",
                "maturity"  : "2025-02-28",
                "lei"       : "R0MUWSFPU8MPRO8K5P83",
                "legal_name": "BNPPARIBAS"
            }
        )
        self.assertEqual(Bond.objects.count(), 1)
        bond_created = Bond.objects.get()
        self.assertEqual(bond_created.isin, "FR0000131104")
        self.assertEqual(bond_created.size, 100000000)
        self.assertEqual(bond_created.currency, "EUR")
        self.assertEqual(bond_created.maturity.isoformat(), "2025-02-28")
        self.assertEqual(bond_created.lei, "R0MUWSFPU8MPRO8K5P83")
        self.assertEqual(bond_created.legal_name, "BNPPARIBAS")

    def test_bonds_list(self):
        # Create the bond
        bond = {
            "isin"    : "FR0000131104",
            "size"    : 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei"     : "R0MUWSFPU8MPRO8K5P83"
        }
        self.client.post("/bonds/", data=bond, format="json")

        # Retrieve it
        resp = self.client.get("/bonds/")
        self.make_assertions(resp, {
            "isin"      : "FR0000131104",
            "size"      : 100000000,
            "currency"  : "EUR",
            "maturity"  : "2025-02-28",
            "lei"       : "R0MUWSFPU8MPRO8K5P83",
            "legal_name": "BNPPARIBAS"
        })

    def test_bond_list_filter(self):
        # Create 2 bonds
        bond1 = {
            "isin"    : "FR0000131104",
            "size"    : 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei"     : "R0MUWSFPU8MPRO8K5P83"
        }
        bond2 = {
            "isin"    : "FR0000151105",
            "size"    : 5000000,
            "currency": "EUR",
            "maturity": "2035-03-30",
            "lei"     : "969500UOFUIQ6PURHN70"
        }
        self.client.post("/bonds/", data=bond1, format="json")
        self.client.post("/bonds/", data=bond2, format="json")

        # Retrieve with filter
        resp = self.client.get("/bonds/?legal_name=BNPPARIBAS")
        self.make_assertions(resp, {
            "isin"      : "FR0000131104",
            "size"      : 100000000,
            "currency"  : "EUR",
            "maturity"  : "2025-02-28",
            "lei"       : "R0MUWSFPU8MPRO8K5P83",
            "legal_name": "BNPPARIBAS"
        })

        resp = self.client.get("/bonds/?isin={}".format(bond2["isin"]))
        self.make_assertions(resp, {
            "isin"      : "FR0000151105",
            "size"      : 5000000,
            "currency"  : "EUR",
            "maturity"  : "2035-03-30",
            "lei"       : "969500UOFUIQ6PURHN70",
            "legal_name": "CREDITAGRICOLECIBTRANSACTIONS"
        })

    def make_assertions(self, resp, compare_to):
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_content = json.loads(resp.content.decode("utf-8"))
        self.assertIsInstance(resp_content, list)
        self.assertEqual(len(resp_content), 1)
        self.assertDictEqual(
            {
                k: v
                for k, v in resp_content[0].items()
                if k != 'url'
            },
            compare_to
        )
