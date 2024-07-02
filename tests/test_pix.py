import sys

sys.path.append("../")

import pytest
import os
from payments.pix import Pix


def test_pix_create_payment():
    pix_instance = Pix()

    payment_info = pix_instance.create_payment(base_dir="../")

    assert "bank_payment_id" in payment_info
    assert "qr_code_path" in payment_info

    os.path.isfile(f"/static/img/{payment_info['qr_code_path']}.png")
