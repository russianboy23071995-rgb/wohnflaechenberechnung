"""Tests für PDF-Formatierung."""

from wohnflaechen.presentation.pdf.formatters import calculation_html, name_html


def test_calculation_html_plus_prefix():
    text = "1,74 m x 3,38 m\n0,24 m x 2,96 m"
    html = str(calculation_html(text))
    assert "1,74 m x 3,38 m" in html
    assert "calc-prefix" in html
    assert "+ 0,24 m x 2,96 m" in html
    assert "<br/>" not in html


def test_calculation_html_no_slash_break():
    text = "1,06 m x 1,46 m / 2"
    html = str(calculation_html(text))
    assert "/ 2" in html
    assert "<br> 2" not in html


def test_round_calculation_numbers():
    from wohnflaechen.presentation.pdf.formatters import round_calculation_text

    assert "1,74 m" in round_calculation_text("1,7400 m x 3,3800 m")


def test_calculation_html_deductions_spacing():
    text = "3,19 m x 4,42 m\nAbzüge und Dachschrägen:\n- 3,45 m x 0,59 m"
    html = str(calculation_html(text))
    assert "calc-section" in html
    assert "Abzüge" in html


def test_calculation_html_deductions():
    text = "3,19 m x 4,42 m\nAbzüge und Dachschrägen:\n- 3,45 m x 0,59 m"
    html = str(calculation_html(text))
    assert "Abzüge" in html
    assert "- 3,45 m x 0,59 m" in html


def test_name_html_slash():
    html = str(name_html("Wohnen / Essen"))
    assert "Wohnen" in html
    assert "Essen" in html
    assert "/" not in html or "<br/>" in html
