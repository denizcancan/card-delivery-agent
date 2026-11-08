from app.assistant.session import speakable
from app.assistant.tts import clean_for_speech


def test_drops_leaked_meta_and_honorifics():
    assert speakable("Teşekkür ederim, Ayşe Hanım...") == "Teşekkür ederim..."
    assert speakable("(no—must avoid gendered address).") == ""
    assert speakable("Let me restate.") == ""
    assert speakable("(hitap kuralı gereği ad soyad kullanıyorum): Teşekkür ederim.") == "Teşekkür ederim."
    assert (speakable("Bilgileri yalnızca hesap sahibi Elif Hanımla paylaşabiliyoruz.")
            == "Bilgileri yalnızca hesap sahibi Elif ile paylaşabiliyoruz.")


def test_keeps_normal_turkish():
    s = "Perşembe sabah dokuzdan öğlen bire kadar uygun mu?"
    assert speakable(s) == s
    assert speakable("Not aldım, teşekkür ederim.") == "Not aldım, teşekkür ederim."


def test_markdown_cleanup():
    assert clean_for_speech("**09:00** - ok") == "09:00 - ok"
    assert clean_for_speech("- Perşembe") == "Perşembe"
