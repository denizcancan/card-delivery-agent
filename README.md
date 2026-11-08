# Freya – Kart Teslim Asistanı (Görev 1)

Kuryenin salı günü ulaşamadığı 8 kredi kartı sahibiyle Türkçe konuşan ve bu hafta için yeni bir teslim zamanı ayarlayan sesli asistan. Müşteriyi sen oynuyorsun; telefon hattı yok, konuşma tarayıcıdan, mikrofonla gerçek zamanlı yapılıyor.

## Çalıştırma

```bash
uv sync
cp .env.example .env          # ELEVENLABS_API_KEY'i doldur
uv run uvicorn app.main:app --port 8000
```

Ardından Chrome'da **http://localhost:8000** adresini aç, mikrofon iznini ver ve bir müşteride "Ara"ya bas.

- **LLM:** Claude Agent SDK, `CLAUDE_CONFIG_DIR` ile seçilen Claude Code hesabının aboneliğini kullanıyor (varsayılan `~/.claude-2`). API anahtarı gerekmiyor.
- **Ses modları:** "Ses" seçicisinde ElevenLabs, tarayıcı sesi ve kapalı (metin) var. Kredi harcamamak için çoğu testi "Kapalı" modda, yazarak yap.
- **Söz kesme:** Asistan konuşurken araya girmeni sağlıyor. Yalnızca kulaklıkla aç. Hoparlörden çıkan ses STT'ye girer, bu yüzden varsayılan olarak asistan konuşurken mikrofon kapanıyor.
- **"Teslimatı iptal et" ve "Sıfırla" düğmeleri:** İptal, bekleme listesindeki müşterinin otomatik terfisini gösteriyor. Sıfırla, demo verisini başa alıyor.

## Mimari

```
Chrome ─ Web Speech API (tr-TR, STT) ──metin──┐
   ▲                                          ▼  WebSocket /ws/call/{id}
   └── PCM ses ◄── ElevenLabs Flash v2.5 ◄── CallSession (Claude Agent SDK, Haiku 5.5)
                    (cümle cümle akış)            │ tool çağrıları (in-process MCP)
                                                  ▼  HTTP
                                         Banka servisi /bank (FastAPI + SQLite)
```

| Klasör | İçerik |
|---|---|
| `app/bank/` | **Banka servisi.** Şema, iş kuralları (`service.py`) ve REST API. OpenAPI dokümanı: `/bank/docs` |
| `app/assistant/` | Arama oturumu (`session.py`), 6 tool (`tools.py`), TTS, prompt yükleyici |
| `static/` | Arayüz: müşteriler, görüşme dökümü, canlı kapasite, bekleme listesi, operasyon talepleri, SMS mock |
| `PROMPTS.md` | Prompt'lar ve gerekçeleri. Kod prompt'ları doğrudan bu dosyadan okuyor |
| `scripts/simulate.py` | 8 senaryoluk uçtan uca test |
| `tests/` | Banka kuralları ve ses filtresi için birim testleri |

## Kararlar ve eklediğim kurallar

- **Kapasite yetmiyor:** 8 müşteriye 7 yer var, Kadıköy'de 3 kişiye 2 yer düşüyor. Sistem fazla rezervasyon yapmıyor. Açıkta kalan müşteri için sıra şöyle:
  1. Bu haftanın bekleme listesi. Yer açılırsa otomatik atanıyor ve SMS gidiyor.
  2. Açılmazsa gelecek haftanın ilk teslimatlarında öncelik.
  3. Müşteri ısrar ederse operasyona kapasite talebi.
- **Güvenceler sunucuda, prompt'ta değil:**
  - Kimlik doğrulanmadan hiçbir tool çalışmıyor.
  - Doğum tarihi LLM'e hiç gönderilmiyor; karşılaştırmayı servis yapıyor ve 2 hatalı denemede kilitliyor.
  - Tool'lar `customer_id` almıyor; müşteri arama başlarken sunucuda oturuma bağlanıyor.
  - Kapasite koşullu `UPDATE` ve `CHECK` kısıtıyla korunuyor. Müşteri başına tek aktif randevu kısmi unique index ile sağlanıyor.
- **Teslim kuralları:**
  - Kart yalnızca sahibine verilir; üçüncü kişiye teslim isteği reddedilir.
  - Telefonu başkası açarsa aramanın konusu söylenmez.
  - Telefonda adres değiştirilmez, istek operasyona devredilir.
- **Sesli kanal güvenlik ağı:** Model iç düşüncesini ya da "Hanım/Bey" hitabını metne sızdırırsa bu parçalar seslendirilmeden atılıyor (`session.py: speakable`).
- **Message queue yok:** Tool çağrısı senkron olmak zorunda; tutarlılığı DB transaction'ı sağlıyor.

## Ölçüm

```bash
uv run pytest                          # 9 birim testi
uv run python scripts/simulate.py -v   # sunucu açıkken: 8 arama + iptal sonrası terfi kontrolü
```

Son koşu **9/9** geçti. LLM'in ilk metne kadarki süresi medyan yaklaşık 1.2 saniye, p90 yaklaşık 1.8 saniye. İlk ses buna yaklaşık 0.5 saniye ekliyor.

Senaryo testi beş şeyi kontrol ediyor:
- Sonucun beklenenle aynı olması
- Kapasitenin aşılmaması
- Telefonu açan üçüncü kişiye kart bilgisi sızmaması
- Adres değişikliği isteğinin operasyona devredilmesi
- Doğrulamanın yapıldığı turda slotlara da bakılması

Prompt'un geliştirme geçmişi ve her değişikliğin hangi bulgudan çıktığı `PROMPTS.md` dosyasında.

## Optimizasyon düğmeleri

| Ne | Nerede |
|---|---|
| Model (`claude-haiku-5-5` / `claude-sonnet-5-5`) | `.env` → `LLM_MODEL`. Sonnet denemede tool çağrılı turlarda belirgin şekilde yavaştı |
| Ses | `.env` → `ELEVENLABS_VOICE_ID`. Free plan yalnızca hazır sesleri kullanabiliyor |
| Konuşmanın bittiğine karar verme süresi | `static/app.js` → `ENDPOINT_MS` (700 ms) |
| Asistan sustuktan sonra mikrofonun açılma süresi | `static/app.js` → `IDLE_MS` (600 ms) |
| Prompt | `PROMPTS.md`; her yeni aramada yeniden okunuyor |

## Bilerek dışarıda bıraktıklarım

- Gerçek telefon hattı (gereksinimde yoktu).
- Gelecek haftanın slotları (yalnızca öncelik bayrağı tutuluyor).
- Söz kesildiğinde LLM üretimini sunucuda durdurmak. Şu an yalnızca kalan ses atılıyor.
- Aynı anda çok sayıda arama. Bunun için geçici tutma (hold) mekanizması ve bir arama planlayıcısı gerekir.

## Gerçek bankada açmadan önce

- **Kimlik doğrulama:** Doğum tarihi tek başına yeterli değil, kolayca bulunabilen bir bilgi. Kayıtlı numaraya OTP ya da uygulamadan push onayı gibi ikinci bir bağımsız bileşen gerekir. Telefon bankacılığında mevzuat iki bileşenli doğrulama istiyor.
- **KVKK:**
  - Chrome STT sesi Google'a gönderiyor; sözleşmeli ya da kurum içi bir STT gerekir.
  - Görüşme başında kayıt ve yapay zekâ bildirimi yapılmalı.
  - `call_events` tablosundaki dökümlerde müşterinin söylediği doğum tarihi duruyor. Bunlar maskelenmeli ve saklama süresi tanımlanmalı.
- **Altyapı:**
  - Claude için abonelik yerine API anahtarı ya da Bedrock/Vertex.
  - Gerçek SMS ve kurye entegrasyonu için outbox tablosunu işleyen bir worker.
  - Denetim kaydı, izleme ve alarm.
- **Kalite:**
  - Senaryo setini büyütmek: aksan, gürültü, kararsız müşteri, sayıların yanlış tanınması.
  - Sabit replikler yerine LLM'in oynadığı müşteri personalarıyla değerlendirme.
  - Bir insan temsilcinin dökümleri örnekleyerek denetlemesi.
