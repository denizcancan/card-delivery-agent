# Freya – Kart Teslim Asistanı (Görev 1)

> **Görev 2 (ürün tasarımı):** [`gorev2/index.html`](gorev2/index.html) dosyasını tarayıcıda aç. Bu tasarım 2 saatlik geliştirme süresi dolduktan sonra hazırlandı; 2 saatin tamamı Görev 1'e gitti.
>
> **AI sohbet kayıtları:** [`ai-sohbetleri/`](ai-sohbetleri/)

Kuryenin salı günü ulaşamadığı 8 kredi kartı sahibiyle Türkçe konuşan ve bu hafta için yeni bir teslim zamanı ayarlayan sesli asistan. Müşteriyi sen oynuyorsun; telefon hattı yok, konuşma tarayıcıdan, mikrofonla gerçek zamanlı yapılıyor.

## Çalıştırma

```bash
uv sync
cp .env.example .env          # ELEVENLABS_API_KEY'i doldur
uv run uvicorn app.main:app --port 8000
```

Ardından Chrome'da **http://localhost:8000** adresini aç, mikrofon iznini ver ve bir müşteride "Ara"ya bas.

> **Safari'de açma.** Safari `webkitSpeechRecognition`'ı tanıyor ama konuşmayı Apple'ın dikte servisine gönderiyor. Sürekli dinleme ve mikrofon izinleri güvenilir değil: mikrofon kesiliyor, izin tekrar tekrar soruluyor. Sayfa Safari'de açılırsa arayüz bir uyarı gösteriyor.

- **LLM:** Claude Agent SDK, `CLAUDE_CONFIG_DIR` ile seçilen Claude Code hesabının aboneliğini kullanıyor (varsayılan `~/.claude-2`). API anahtarı gerekmiyor.
- **Ses modları:** "Ses" seçicisinde ElevenLabs, tarayıcı sesi ve kapalı (metin) var. Kredi harcamamak için çoğu testi "Kapalı" modda, yazarak yap.
- **Söz kesme:** Asistan konuşurken araya girmeni sağlıyor. Yalnızca kulaklıkla aç. Hoparlörden çıkan ses STT'ye girer, bu yüzden varsayılan olarak asistan konuşurken mikrofon kapanıyor.
- **Mikrofon:**
  - İzin isteminde kalıcı izin seçeneğini seç, "Bu sefer izin ver"i değil. Tek seferlik izin düşünce Chrome konuşma tanımayı sessizce kapatıyor.
  - Sayfayı hep aynı adresten aç (`localhost:8000`).
  - Mikrofonu yalnızca Chrome'un konuşma tanıması açıyor. Yanındaki çubuk tanımanın olaylarını gösteriyor: kısa çubuk mikrofonun açık olduğunu, yarım çubuk ses algılandığını, dolu çubuk konuşma algılandığını belirtiyor. Ayrı bir `getUserMedia` akışı denendi ama macOS'ta hem sesi hem mikrofonu bozduğu için kaldırıldı.
  - macOS'ta "audio-capture" hatası görürsen Sistem Ayarları → Gizlilik ve Güvenlik → Mikrofon altında Chrome'un açık olduğunu kontrol et.
  - Durum etiketi tıklanabilir; tıklayınca mikrofon yeniden deneniyor. Sekme arka plana geçince konuşma tanıma duruyor, geri dönünce kendiliğinden açılıyor.
  - Sorun olursa `localhost:8000/?debug` ile aç ve konsoldaki `[stt]` satırlarına bak.
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
| `app/assistant/` | Arama oturumu (`session.py`), 10 tool (`tools.py`), TTS, prompt yükleyici |
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
- **Adres teyidi, zaman ayarlamadan önce:** Kurye salı günü müşteriyi adreste bulamadı. Bu yüzden asistan önce kayıtlı adresi okuyup teyit alıyor; servis de teyit olmadan slot listelemiyor.
  - **Müşteri başka bir adres söylerse:** Asistan adresi ve ilçeyi alıyor, ardından iki seçenek sunuyor: kayıtlı adres de güncellensin ya da yeni adres yalnızca bu teslimat için kullanılsın.
  - **Slotlar teslimat adresine göre geliyor:** Boş zamanlar yeni adresin ilçesinden listeleniyor. Kuryenin bu hafta gitmediği bir ilçe söylenirse gidilen ilçeler sayılıyor ve gelecek hafta önceliği öneriliyor.
  - **Güvenlik önlemleri:** Kartı başka bir adrese yönlendirmek bilinen bir dolandırıcılık yöntemi. Bu yüzden adres değişikliği yalnızca kimlik doğrulandıktan sonra yapılabiliyor. Her değişiklik `address_changes` tablosuna yazılıyor ve kayıtlı numaraya "siz yapmadıysanız bize ulaşın" SMS'i gidiyor. Alıcı değişikliğine hâlâ izin yok.
- **Görüşme içinde değişiklik ve iptal:**
  - Randevu, aynı görüşmede başka bir boş zamana taşınabiliyor. Taşıma atomik: yeni yer alınmadan eskisi bırakılmıyor.
  - Müşteri iptal isterse önce bir kez teyit alınıyor, sonra iptal ediliyor.
  - Boşalan yer bekleme listesindeki ilk uygun kişiye hemen geçiyor. Tool sonucunda o kişinin adı yer almıyor.
- **Teslim kuralları:**
  - Kart yalnızca sahibine verilir; üçüncü kişiye teslim isteği reddedilir.
  - Telefonu başkası açarsa aramanın konusu söylenmez.
- **Sokak adresleri uydurma:** Case yalnızca ilçe ve adres tipini (ev / iş yeri) veriyor; sokak adresleri demo için uydurulmuş örnek verilerdir.
- **Sesli kanal güvenlik ağı:** Model iç düşüncesini ya da "Hanım/Bey" hitabını metne sızdırırsa bu parçalar seslendirilmeden atılıyor (`session.py: speakable`).
- **Message queue yok:** Tool çağrısı senkron olmak zorunda; tutarlılığı DB transaction'ı sağlıyor.

## Ölçüm

```bash
uv run pytest                          # 14 birim testi
uv run python scripts/simulate.py -v   # sunucu açıkken: 8 arama + iptal sonrası terfi kontrolü
```

Son koşu **9/9** geçti. LLM'in ilk metne kadarki süresi medyan yaklaşık 1.4 saniye, p90 yaklaşık 1.9 saniye. İlk ses buna yaklaşık 0.5 saniye ekliyor.

Senaryolar:
- Ayşe aynı görüşmede perşembeden cumaya geçiyor.
- Kadıköy dolu, Zeynep bekleme listesine giriyor.
- Burak'ın yeni adresi Ataşehir'de ve kayıtlı adresini de güncelletiyor.
- Selin randevu alıp vazgeçiyor.
- Can doğum tarihini iki kez yanlış söylüyor.
- Elif'in telefonunu eşi açıyor.
- Ali kartı iş arkadaşına bırakmak istiyor.

Her senaryoda şunlar kontrol ediliyor:
- Sonuç beklenenle aynı mı?
- Kapasite aşıldı mı?
- Telefonu açan üçüncü kişiye kart ya da adres bilgisi sızdı mı?
- Adres teyidi yapıldı mı?
- Değişiklik, iptal ve adres güncellemesi DB'ye doğru yansıdı mı?
- Adresin teyit edildiği turda slotlara da bakıldı mı?

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
- Adres doğrulama ve coğrafi kodlama. İlçeyi LLM müşterinin cümlesinden çıkarıyor; adresin gerçekten var olup olmadığı kontrol edilmiyor.

## Gerçek bankada açmadan önce

- **Kimlik doğrulama:** Doğum tarihi tek başına yeterli değil, kolayca bulunabilen bir bilgi. Kayıtlı numaraya OTP ya da uygulamadan push onayı gibi ikinci bir bağımsız bileşen gerekir. Telefon bankacılığında mevzuat iki bileşenli doğrulama istiyor.
- **Adres değişikliği:** Bu iki bileşenli doğrulama olmadan riskli; kayıtlı adres güncellemesi için en azından OTP şart. Yeni adres bir adres doğrulama servisinden geçmeli. Kısa sürede yapılan adres değişikliği ve teslimat bir dolandırıcılık sinyali olarak işaretlenmeli.
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
