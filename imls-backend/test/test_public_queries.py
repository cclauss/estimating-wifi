import datetime
import os
import pytz
import requests
from unittest import TestCase


def endpoint(ep_arr):
    test_url = f"{os.getenv('PYTEST_SCHEME')}://{os.getenv('PYTEST_HOSTNAME')}:{os.getenv('PYTEST_PORT')}"
    return test_url + "/" + "/".join(ep_arr)


class PresencesTests(TestCase):
    # NOTE: There's a ?limit parameter on these, because otherwise a lot of
    # values come back by default, and that makes for  slow tests.
    def test_existence_of_presences(self):
        url = endpoint(["presences?limit=25"])
        response = requests.get(url)
        if response.status_code != 200:
            print(response.json())
        self.assertTrue(response.status_code == 200)

    def test_presences_is_big(self):
        url = endpoint(["presences?limit=25"])
        headers = {"Prefer": "count=estimated"}
        response = requests.get(url, headers=headers)
        estimated_count = int(response.headers["Content-Range"].split("/")[1])
        self.assertGreater(estimated_count, 100)


def validate(test_obj, fscs_id):
    url = endpoint(["rpc", "lib_search_fscs"])
    query = {"_fscs_id": fscs_id}
    r = requests.post(url, json=query)
    obj = r.json()
    test_obj.assertEqual(obj["fscskey"], fscs_id.split("-")[0])


class LibSearchTests(TestCase):
    def test_validate_one(self):
        url = endpoint(["rpc", "lib_search_fscs"])
        query = {"_fscs_id": "KY0069-002"}
        r = requests.post(url, json=query)
        print(r.json())
        obj = r.json()
        self.assertEqual(obj['fscs_id'], "KY0069-002")


    # First, this takes forever.
    # Second, I generated the list of FSCS Ids from the DB itself.
    # That means they're all "good." This loop tests that my list
    # came from the DB, and is still there. Not useful.
    # def test_validate_all(self):
    #     for line in open("all_fscs_ids.txt"):
    #         self.assertEqual(len(line.strip()), 10)
    #         validate(self, line.strip())

class LibSearchNameTests(TestCase):
    def test_validate_one(self):
        url = endpoint(["rpc", "lib_search_name"])
        query = {"_name": "STRAWBERRY POINT PUB"}
        r = requests.post(url, json=query)
        print(r.json())
        obj = r.json()
        self.assertEqual(obj[0]['fscs_id'], "IA0141-002")

class LibSearchStateTests(TestCase):
    def test_validate_one(self):
        url = endpoint(["rpc", "lib_search_state"])
        query = {"_state_code": "AK"}
        r = requests.post(url, json=query)
        print(r.json())
        obj = r.json()
        self.assertEqual(obj[0]['fscs_id'], "AK0001-002")


class BinningTests(TestCase):
    def test_no_data(self):
        # _start date, _fscs_id text, _direction boolean, _days integer
        url = endpoint(["rpc", "bin_devices_over_time"])
        query = {
            "_fscs_id": "KY0069-002",
            "_start": "2022-02-02",
            "_direction": True,
            "_days": 7,
        }
        r = requests.post(url, json=query)
        print(r.json())
        res = r.json()
        # This should return 7 lists of length 24, each containing all zeros.
        self.assertEqual(7, len(res))
        map(lambda ls: self.assertEqual(len(ls), 24), res)
        map(lambda ls: map(lambda v: self.assertEqual(v, 0), ls), res)

    def test_actual_over_time(self):
        url = endpoint(["rpc", "bin_devices_over_time"])
        query = {
            "_fscs_id": "GA0029-004",
            "_start": "2022-05-11",
            "_direction": True,
            "_days": 7,
        }
        r = requests.post(url, json=query)
        print(r.json())
        res = r.json()
        self.assertEqual(7, len(res))
        filtered = [
            [
                18,
                12,
                12,
                12,
                18,
                12,
                0,
                30,
                78,
                156,
                222,
                216,
                132,
                150,
                174,
                264,
                408,
                444,
                306,
                72,
                6,
                6,
                12,
                12,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                246,
                306,
                306,
                264,
                318,
                342,
                372,
                312,
                228,
                36,
                12,
                18,
                24,
                12,
            ],
            [
                12,
                18,
                12,
                24,
                18,
                6,
                6,
                90,
                90,
                150,
                168,
                222,
                258,
                270,
                288,
                228,
                78,
                6,
                0,
                6,
                0,
                0,
                6,
                6,
            ],
            [
                12,
                24,
                24,
                24,
                18,
                12,
                12,
                24,
                42,
                78,
                90,
                120,
                126,
                114,
                132,
                156,
                42,
                0,
                0,
                0,
                18,
                18,
                24,
                18,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                114,
                132,
                144,
                138,
                138,
            ],
            [
                12,
                30,
                30,
                30,
                24,
                18,
                18,
                84,
                114,
                168,
                180,
                198,
                240,
                264,
                300,
                306,
                354,
                300,
                174,
                12,
                18,
                12,
                18,
                18,
            ],
            [
                6,
                36,
                48,
                12,
                18,
                12,
                12,
                108,
                198,
                318,
                432,
                468,
                456,
                462,
                468,
                474,
                570,
                474,
                318,
                150,
                30,
                30,
                24,
                12,
            ],
        ]
        self.assertEqual(res, filtered)

    def test_actual_per_hour(self):
        url = endpoint(["rpc", "bin_devices_per_hour"])
        query = {"_fscs_id": "GA0029-004", "_start": "2022-05-11"}
        r = requests.post(url, json=query)
        print(r.json())
        res = r.json()
        self.assertEqual(24, len(res))
        filtered = [
            18,
            12,
            12,
            12,
            18,
            12,
            0,
            30,
            78,
            156,
            222,
            216,
            132,
            150,
            174,
            264,
            408,
            444,
            306,
            72,
            6,
            6,
            12,
            12,
        ]
        self.assertEqual(res, filtered)
