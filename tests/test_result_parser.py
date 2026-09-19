import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracuumst import result_parser
from tracuumst.models import TrangThai

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_thanh_cong():
    html = (FIXTURES / "sample_result_thanh_cong.html").read_text(encoding="utf-8")
    ket_qua = result_parser.parse(html, "001203000001")

    assert ket_qua.trang_thai == TrangThai.THANH_CONG
    assert ket_qua.mst == "8888888888"
    assert ket_qua.ho_ten == "Nguyễn Văn Mẫu"
    assert ket_qua.co_quan_thue == "Chi cục thuế khu vực mẫu"
    assert ket_qua.dia_chi is None


def test_parse_khong_tim_thay():
    html = (FIXTURES / "sample_result_khong_tim_thay.html").read_text(encoding="utf-8")
    ket_qua = result_parser.parse(html, "999999999999")

    assert ket_qua.trang_thai == TrangThai.KHONG_TIM_THAY
    assert ket_qua.mst is None


def test_parse_html_rong():
    ket_qua = result_parser.parse("<html><body></body></html>", "123456789")
    assert ket_qua.trang_thai == TrangThai.KHONG_TIM_THAY
