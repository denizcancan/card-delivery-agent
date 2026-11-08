from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest

from app.bank.service import Bank, BankError

DOB = {1: "1988-03-14", 2: "1975-11-02", 3: "1993-06-27", 4: "1981-01-09"}
KADIKOY_THU, KADIKOY_FRI, ATASEHIR_THU = 1, 2, 3


@pytest.fixture
def bank(tmp_path):
    b = Bank(tmp_path / "t.db", date(2026, 11, 11))
    b.init()
    return b


def verified_call(bank, customer_id):
    call_id = bank.start_call(customer_id)["call_id"]
    assert bank.verify_identity(call_id, DOB[customer_id])["verified"]
    return call_id


def test_seed_dates_and_capacity(bank):
    board = bank.board()
    assert board["totals"] == {"customers": 8, "capacity": 7}
    assert {s["date"] for s in board["slots"]} == {"2026-11-12", "2026-11-13"}


def test_tools_require_verification(bank):
    call_id = bank.start_call(1)["call_id"]
    for fn in (lambda: bank.list_slots(call_id), lambda: bank.book_slot(call_id, KADIKOY_THU),
               lambda: bank.join_waitlist(call_id, [])):
        with pytest.raises(BankError) as e:
            fn()
        assert e.value.code == "not_verified"


def test_verification_accepts_turkish_format_and_locks_after_two_failures(bank):
    call_id = bank.start_call(1)["call_id"]
    assert bank.verify_identity(call_id, "14.03.1988")["verified"]

    call_id = bank.start_call(2)["call_id"]
    assert bank.verify_identity(call_id, "1975-01-01") == {"ok": True, "verified": False, "attempts_left": 1}
    assert bank.verify_identity(call_id, "1975-01-02")["locked"]
    with pytest.raises(BankError) as e:
        bank.verify_identity(call_id, DOB[2])  # doğru tarih bile artık kabul edilmez
    assert e.value.code == "locked"
    assert bank.end_call(call_id)["outcome"] == "verification_failed"


def test_kadikoy_overflow_waitlist_and_promotion(bank):
    a = verified_call(bank, 1)
    assert bank.book_slot(a, KADIKOY_THU)["booked"]
    m = verified_call(bank, 2)
    assert bank.book_slot(m, KADIKOY_FRI)["booked"]

    z = verified_call(bank, 3)
    slots = bank.list_slots(z)
    assert slots["slots"] == [] and slots["overflow"]["reason"] == "district_full"
    with pytest.raises(BankError) as e:
        bank.book_slot(z, KADIKOY_THU)
    assert e.value.code == "slot_full"
    assert bank.join_waitlist(z, [KADIKOY_THU, KADIKOY_FRI])["position"] == 1
    assert bank.end_call(z)["outcome"] == "waitlisted"

    appt = bank.board()["customers"][0]["appointment"]["appointment_id"]
    res = bank.cancel_appointment(appt)
    assert res["promoted"]["full_name"] == "Zeynep Arslan"
    statuses = {c["full_name"]: c["status"] for c in bank.board()["customers"]}
    assert statuses["Zeynep Arslan"] == "scheduled" and statuses["Ayşe Kaya"] == "pending"


def test_guards_wrong_district_double_booking_and_premature_waitlist(bank):
    a = verified_call(bank, 1)
    with pytest.raises(BankError) as e:
        bank.book_slot(a, ATASEHIR_THU)
    assert e.value.code == "wrong_district"
    with pytest.raises(BankError) as e:
        bank.join_waitlist(a, [])
    assert e.value.code == "slots_available"
    bank.book_slot(a, KADIKOY_THU)
    with pytest.raises(BankError) as e:
        bank.book_slot(a, KADIKOY_FRI)
    assert e.value.code == "already_booked"


def test_concurrent_booking_never_exceeds_capacity(bank):
    calls = [verified_call(bank, cid) for cid in (1, 2, 3)]

    def attempt(call_id):
        try:
            return bank.book_slot(call_id, KADIKOY_THU)["booked"]
        except BankError as e:
            return e.code

    with ThreadPoolExecutor(3) as pool:
        results = list(pool.map(attempt, calls))
    assert results.count(True) == 1 and results.count("slot_full") == 2
